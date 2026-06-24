echo '#!/bin/sh
exec viewnior "$@"' > usr/local/bin/defaultimageviewer
chmod 755 usr/local/bin/defaultimageviewer

if [ ! -e usr/local/apps/ROX-Filer/AppRun ]; then
	for T in `grep ^MimeType= usr/share/applications/viewnior.desktop | sed -e s/^MimeType=//g -e 's/;/ /g'`; do
		[ "$T" = "image/bmp" ] && continue
		chroot . xdg-mime default viewnior.desktop $T
		chroot . run-as-spot xdg-mime default viewnior.desktop $T
	done
fi

if [ -f usr/bin/labwc ]; then
	mv -f usr/bin/viewnior usr/bin/viewnior.bin
	echo '#!/bin/sh
# Simple launch wrapper for the viewnior image viewer.
# Image panning fails with some GTK themes in Wayland
# so we force the x11 environment via GDK_BACKEND=x11.

exec env GDK_BACKEND=x11 /usr/bin/viewnior.bin "$@"' > usr/bin/viewnior
	chmod 755 usr/bin/viewnior
fi
