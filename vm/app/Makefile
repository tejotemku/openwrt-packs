include $(TOPDIR)/rules.mk

PKG_NAME:=cmd_app
PKG_VERSION:=1.0.0
PKG_RELEASE:=1
PKG_LICENSE:=GPL-2.0-or-later
PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)-$(PKG_VERSION)

include $(INCLUDE_DIR)/package.mk

define Package/cmd_app
  SECTION:=base
  CATEGORY:=Sound
  TITLE:=cmd_app
  MAINTAINER:=Marcel Jarosz
endef


define Package/cmd_app/description
	App files copy
endef

define Build/Prepare
endef

define Build/Configure
endef

define Build/Compile
	echo 'BUILD'
endef

define Package/cmd_app/install
	$(INSTALL_DIR) $(1)/root/
	$(CP) ./files/root/* $(1)/root/
endef

$(eval $(call BuildPackage,cmd_app))
