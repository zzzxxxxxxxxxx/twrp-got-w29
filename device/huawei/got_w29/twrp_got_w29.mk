$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/aosp_base.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/gsi_keys.mk)

$(call inherit-product, vendor/twrp/config/common.mk)
$(call inherit-product, device/huawei/got_w29/device.mk)

PRODUCT_DEVICE := got_w29
PRODUCT_NAME := twrp_got_w29
PRODUCT_BRAND := Huawei
PRODUCT_MODEL := GOT-W29
PRODUCT_MANUFACTURER := Huawei
PRODUCT_RELEASE_NAME := GOT-W29

