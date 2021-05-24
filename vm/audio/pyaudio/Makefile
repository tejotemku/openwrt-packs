include $(TOPDIR)/rules.mk

PKG_NAME:=cmd_app
PKG_VERSION:=1.0.0
PKG_RELEASE:=1
PKG_LICENSE:=GPL-2.0-or-later
PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)-$(PKG_VERSION)

include $(INCLUDE_DIR)/package.mk

define Package/pyaudio
  SECTION:=base
  CATEGORY:=Sound
  TITLE:=pyaudio
  MAINTAINER:=Marcel Jarosz
endef


define Package/pyaudio/description
	pyaudio files copy
endef

define Build/Prepare
endef

define Build/Configure
endef

define Build/Compile
	echo 'BUILD'
endef

define Package/pyaudio/install
	$(INSTALL_DIR) $(1)/root/
	$(CP) ./files/* $(1)/root/
endef

$(eval $(call BuildPackage,pyaudio))
