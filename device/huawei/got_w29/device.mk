PRODUCT_SHIPPING_API_LEVEL := 31
PRODUCT_USE_DYNAMIC_PARTITIONS := true

$(call inherit-product, $(SRC_TARGET_DIR)/product/emulated_storage.mk)

# Keep the recovery keymaster client available for FBE metadata decryption.
PRODUCT_PACKAGES += \
    android.hardware.keymaster@4.1 \
    android.hardware.health@2.1-service \
    android.system.keystore2

TARGET_RECOVERY_DEVICE_MODULES += \
    android.hardware.keymaster@4.1

TW_RECOVERY_ADDITIONAL_RELINK_LIBRARY_FILES += \
    $(TARGET_OUT_SHARED_LIBRARIES)/android.hardware.keymaster@4.1.so

