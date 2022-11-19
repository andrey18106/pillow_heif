# https://github.com/Homebrew/homebrew-core/blob/master/Formula/libheif.rb

class Libheif < Formula
  desc "ISO/IEC 23008-12:2017 HEIF file format decoder and encoder"
  homepage "https://www.libde265.org/"
  url "https://github.com/strukturag/libheif/releases/download/v1.14.0/libheif-1.14.0.tar.gz"
  sha256 "9a2b969d827e162fa9eba582ebd0c9f6891f16e426ef608d089b1f24962295b5"
  license "LGPL-3.0-only"
  # Set current revision from what it was taken plus 10
  revision 10

  depends_on "pkg-config" => :build
  depends_on "jpeg-turbo"
  depends_on "libde265"
  depends_on "libpng"
  depends_on "shared-mime-info"

  # (001) AOM: remove extend_padding_to_size
  patch do
    url "https://github.com/strukturag/libheif/commit/a01baccaf40bafcabddba47846f5e914ca0724f6.diff"
    sha256 "900c2f1323002af1c6969ae1f9b4a50fe685374e203d034842ee53cb428179ea"
  end

  def install
    system "./configure", *std_configure_args, "--disable-silent-rules"
    system "make", "install"
    pkgshare.install "examples/example.heic"
    pkgshare.install "examples/example.avif"
  end

  def post_install
    system Formula["shared-mime-info"].opt_bin/"update-mime-database", "#{HOMEBREW_PREFIX}/share/mime"
  end
end
