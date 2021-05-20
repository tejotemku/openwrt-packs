#
# Copyright (C) 2007-2018 OpenWrt.org
#
# This is free software, licensed under the GNU General Public License v2.
# See /LICENSE for more information.
#

include $(TOPDIR)/rules.mk

PKG_NAME:=flaccod
PKG_VERSION:=1.0.0
PKG_RELEASE:=1
PKG_SOURCE:=1.3.3.tar.gz
PKG_SOURCE_URL:=https://github.com/xiph/flac/archive/refs/tags/
PKG_HASH:=668cdeab898a7dd43cf84739f7e1f3ed6b35ece2ef9968a5c7079fe9adfe1689

PKG_BUILD_DIR=$(BUILD_DIR)/$(PKG_NAME)-$(BUILD_VARIANT)/flac-1.3.3
PKG_FIXUP:=autoreconf

include $(INCLUDE_DIR)/package.mk

define Package/flaccod
  SECTION:=base
  CATEGORY:=Sound
  TITLE:=flaccod
  MAINTAINER:=Marcel Jarosz
  DEPENDS:=+libflac +libc +libstdcpp
endef

CONFIGURE_ARGS += \
	--disable-ogg \
	--disable-oggtest


define Package/flaccod/description
	Flaccod
endef


define Build/Compile
	$(MAKE) -C $(PKG_BUILD_DIR) DESTDIR="$(PKG_INSTALL_DIR)" install
endef

define Build/InstallDev
	$(INSTALL_DIR) $(1)/usr/include
	$(CP) $(PKG_INSTALL_DIR)/usr/include/* $(1)/usr/include/
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/* $(1)/usr/lib/
endef

define Package/flaccod/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(CP) $(PKG_INSTALL_DIR)/usr/bin/* $(1)/usr/bin/
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/* $(1)/usr/lib/
	$(INSTALL_DIR) $(1)/usr/man
	$(CP) $(PKG_INSTALL_DIR)/usr/man/* $(1)/usr/man/
endef


$(eval $(call BuildPackage,flaccod))
