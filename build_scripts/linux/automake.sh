NAME=$(basename "$BASH_SOURCE" | cut -f 1 -d '.')
cd /host/build-stuff || exit 2
if [[ -d "$NAME-$1" ]]; then
  echo "Cache found for $NAME, install it..."
  cd "$NAME-$1" || exit 102
else
  echo "No cache found for $NAME, build it..."
  wget -q --no-check-certificate -O "$NAME.tar.gz" "https://ftp.gnu.org/gnu/automake/$NAME-$1.tar.gz" \
  && tar xf "$NAME-$1.tar.gz" \
  && rm -f "$NAME-$1.tar.gz" \
  && cd "$NAME-$1" \
  && ./configure \
  && make -j4
fi
make install \
&& automake --version