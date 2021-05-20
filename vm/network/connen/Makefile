#
# Copyright (C) 2007-2018 OpenWrt.org
#
# This is free software, licensed under the GNU General Public License v2.
# See /LICENSE for more information.
#

include $(TOPDIR)/rules.mk

PKG_NAME:=connen
PKG_VERSION:=1.0.0
PKG_RELEASE:=1
PKG_LICENSE:=GPL-2.0-or-later
PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)-$(PKG_VERSION)

include $(INCLUDE_DIR)/package.mk

define Package/connen
  SECTION:=base
  CATEGORY:=Network
  TITLE:=connen
  MAINTAINER:=Marcel Jarosz
endef


define Package/connen/description
	DHCP ON
endef

define Build/Prepare
endef

define Build/Configure
endef

define Build/Compile
	echo 'BUILD'
endef

define Package/connen/install
	$(INSTALL_DIR) $(1)/etc/init.d
	$(CP) ./files/etc/init.d/* $(1)/etc/init.d/
endef

$(eval $(call BuildPackage,connen))
