VERSION="3.3"
NAME=$(basename "$0" | cut -f 1 -d '.')
URL="ftp://sourceware.org/pub/libffi/$NAME-$VERSION.tar.gz"
cd "/host/$BUILD_STUFF" || exit 2
if [[ -d "$NAME" ]]; then
  echo "Cache found for $NAME, install it..."
  cd "$NAME" || exit 102
else
  echo "No cache found for $NAME, build it..."
  mkdir "$NAME"
  wget -q --no-check-certificate -O "$NAME.tar.gz" "$URL" \
  && tar xf "$NAME.tar.gz" -C "$NAME" --strip-components 1 \
  && rm -f "$NAME.tar.gz" \
  && cd "$NAME" \
  && ./configure --prefix /usr \
  && make -j4
fi
make install
if [[ ! -v LDCONFIG_ARG ]]; then
  ldconfig
else
  ldconfig "$LDCONFIG_ARG"
fi