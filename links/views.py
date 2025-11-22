from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404, redirect
from django.db.models import F
from django.utils import timezone
from django.http import HttpResponseNotFound
from nanoid import generate
from .models import Link
from .serializers import LinkSerializer, LinkCreateSerializer
import re
import logging

logger = logging.getLogger(__name__)

CODE_REGEX = re.compile(r'^[A-Za-z0-9]{6,8}$')


@api_view(['GET'])
def healthz(request):
    """Healthcheck endpoint."""
    return Response({'ok': True, 'version': '1.0'})


@api_view(['POST'])
def create_link(request):
    """
    Create a new short link.
    Request JSON:
      { "target": "https://...", "code": "optional6to8chars" }
    """
    serializer = LinkCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    code = data.get('code') or generate('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', 6)
    target = data['target']

    if code and not CODE_REGEX.match(code):
        return Response({'error': 'code must match /^[A-Za-z0-9]{6,8}$/'}, status=status.HTTP_400_BAD_REQUEST)

    # If code exists (and not deleted) -> 409
    if Link.objects.filter(code=code, deleted=False).exists():
        return Response({'error': 'code already exists'}, status=status.HTTP_409_CONFLICT)

    link = Link.objects.create(code=code, target_url=target)
    out = LinkSerializer(link).data
    return Response(out, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def list_links(request):
    """List all non-deleted links."""
    qs = Link.objects.filter(deleted=False).order_by('-created_at')
    serializer = LinkSerializer(qs, many=True)
    return Response(serializer.data)


@api_view(['GET', 'DELETE'])
def link_detail(request, code):
    """
    GET: return stats for a single link.
    DELETE: soft-delete the link (set deleted=True).
    Using one view for both methods allows DRF browsable UI to show DELETE button.
    """
    if request.method == 'GET':
        link = get_object_or_404(Link, code=code, deleted=False)
        serializer = LinkSerializer(link)
        return Response(serializer.data)

    # DELETE
    updated = Link.objects.filter(code=code, deleted=False).update(deleted=True)
    if not updated:
        return Response({'error': 'not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response({"ok": True}, status=status.HTTP_200_OK)


def redirect_view(request, code):
    """
    Redirect route: GET /<code>
    - If found and not deleted: atomically increment clicks and update last_clicked, then 302 to target.
    - If not found: return 404.
    """
    try:
        link = Link.objects.get(code=code, deleted=False)
    except Link.DoesNotExist:
        logger.debug("redirect_view: code not found: %s", code)
        return HttpResponseNotFound('Not Found')

    # Debug log before update
    logger.debug("redirect_view BEFORE update: code=%s clicks=%s target=%s", code, link.clicks, link.target_url)

    # Atomic update
    Link.objects.filter(code=code).update(clicks=F('clicks') + 1, last_clicked=timezone.now())

    # Optionally refresh for logging
    try:
        link.refresh_from_db()
        logger.debug("redirect_view AFTER update: code=%s clicks=%s", code, link.clicks)
    except Exception:
        logger.exception("Failed to refresh link after update for code=%s", code)

    # Perform 302 redirect
    return redirect(link.target_url, permanent=False)