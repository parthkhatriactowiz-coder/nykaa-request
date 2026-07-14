import json
import time
from pathlib import Path
import requests

base_url = "https://www.nykaa.com/"
API_URL = "https://www.nykaa.com/app-api/index.php/products/list"

# Copy the full headers dict (incl. Cookie) from your get-page.py here.
# NOTE: cookies/csrf-token/bm_sz/_abck are session-bound and expire —
# if you start getting empty/blocked responses, grab fresh ones from
# your browser's Network tab and paste them in again.
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "newrelic": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjEyMjUxNTkiLCJhcCI6IjEwMDE0NzQ3MTciLCJpZCI6IjU1NjQ1ZDU2YzFlNDg1YzIiLCJ0ciI6ImIwNjk0M2JiMDEyY2M3ODA4NWI0ODU2NmIzNjJmMzAwIiwidGkiOjE3ODQwMjMwNjI0MzR9fQ==",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://www.nykaa.com/brands/foxtale/c/27361?page_no=6&sort=popularity",
    "sec-ch-ua": '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "traceparent": "00-b06943bb012cc78085b48566b362f300-55645d56c1e485c2-01",
    "tracestate": "1225159@nr=0-1-1225159-1001474717-55645d56c1e485c2----1784023062434",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    "x-csrf-token": "ODByU2gnoiahjyt5",
    "x-newrelic-id": "undefined",
    "Cookie": 'run=75; EXP_REVIEW_COLLECTION=1; D_LST=1; D_PDP=1; bcookie=d62314e2-1f7f-4fbb-b370-ea861a643340; EXP_OL=DEFAULT; EXP_AB_NEW_SHOPPING_BAG=A; PHPSESSID=b4NWWUSz5i5iaAJ1784007754538; PRIVE_TIER=null; head_data_react={"id":"","nykaa_pro":false,"group_id":""}; pro=false; EXP_H_F_M_M_S_P=1; EXP_C_W_P_M=1; EXP_H_F_M_W=1; EXP_H_F_M_S=1; EXP_H_F_M_P_S=1; _gcl_au=1.1.992946926.1784007756; WZRK_G=3b707b7536b944459bc3c72be2b7676b; _gid=GA1.2.1111454385.1784007756; _clck=m7s6vx%5E2%5Eg7q%5E0%5E2386; _pin_unauth=dWlkPU1qSXpORE0wTlRRdFlUUTFOaTAwTkRobUxUZ3hOemd0WkRNM056TmxNbU5qTUdNdw; EXP_AB_CAB_VERTICAL=DEFAULT; EXP_AB_SAVINGS_SHELF=DEFAULT; EXP_AB_NYKAA_NOW_RAAP=A; EXP_AB_NYKAA_NOW_CART=A; EXP_AB_NYKAA_NOW_FILTER=DEFAULT; EXP_AB_CART_OFFERS=A; EXP_AB_PARTIAL_CHECKOUT=A; EXP_AB_EMAIL_VERIFICATION_REVAMP=A; EXP_AB_DWEB_SHOPPING_BAG_URL=A; EXP_NEW_SIGN_UP=DEFAULT; EXP_CART_GRATIFICATION_POPUP=B; EXP_ITEM_DISCOUNT=A; EXP_ORDERS_REVAMP=A; EXP_CART_LOGIN_SEGMENT=A; EXP_ADP_RV_REORDER=B; EXP_AB_CP_GAMES=A; EXP_ADP_RV_SEGMENT=A; EXP_AB_AUTOFILL=B; EXP_ADP_RV_VIEW_SIMILAR_HLP=A; EXP_ADP_RV_VIEW_SIMILAR=A; EXP_ADP_RV_PRODUCT_V3=CONTROL; EXP_AB_HLP_CARD_REVAMP=CONTROL; EXP_AB_WISHLIST=A; EXP_AB_PRICE_REVEAL_NEW=A; EXP_PLP_INLINE_FILTER=REVAMPED; EXP_EDD_DELIVERY_WIDGET=A; EXP_ADP_RV_MULTI_COUPONS=A; EXP_AB_DWEB_MULTICOUPON=A; EXP_ADP_RV_SEARCH_BAR_NEW=A; EXP_AB_AUTH_DWEB=A; EXP_PLP_INLINE_WIDGETS=A; EXP_PLP_PINKBOX_CTA=CONTROL; EXP_QUERY_PARAM_EXP=C; EXP_AB_PDP_IMAGE=DEFAULT; EXP_AB_CALLOUT_NUDGE=A; EXP_AB_TRUECALLER=DEFAULT; EXP_AB_GOOGLE_ONE_TAP=DEFAULT; EXP_AB_HLP_PAGE=A; EXP_AB_SIZE_MINI_PRODUCT=A; EXP_AB_TOP_NAV_CONFIG=CONTROL; EXP_QUERY_PARAM_EXP_DWEB=CONTROL; EXP_AB_HP_SEARCH_ANIMATION=CONTROL; EXP_AB_PDP_HAMBURGER=CONTROL; EXP_AB_HLP_OFFERS=DEFAULT; EXP_AB_WEB_AUTOREAD_OTP=DEFAULT; EXP_AD_BRV=random; EXP_PDP_RELEVANT_CATEGORY=DEFAULT; EXP_AB_REMOVE_LOGIN_BOTTOMSHEET=DEFAULT; EXP_AB_ZENDESK_CHAT=A; EXP_AB_HORIZONTAL_WIDGET_TYPE=CONTROL; EXP_AB_IOC_CART_NUDGE=DEFAULT; EXP_APPSFLYER_DOWNLOAD_CTA=DEFAULT; EXP_AB_PDP_SIMILAR_PRODUCT_SHEET=DEFAULT; EXP_FULL_SCREEN_RECO_WIDGET=DEFAULT; EXP_AB_BEST_SELLER_PDP=A; EXP_AB_ENABLE_HLP_NEW_API=DEFAULT; EXP_SPECULATIVE_PRERENDERING=CONTROL; EXP_AB_TAGS_RATING_ON_LISTING=ONLY_TAGS; EXP_SEARCH_INP_ON_CART=A; EXP_AB_NEW_TAGS_ON_PDP=A; EXP_REVIEW_SUBMIT=A; EXP_AB_OFFER_DELTA_COMMUNICATION=A; EXP_AB_NEW_GC_PAGE=A; EXP_PLP_DNW_DWEB=A; EXP_ERROR_BOUNDARY=DEFAULT; EXP_PRIVE_CTA_DISABLE=DEFAULT; EXP_AB_GETAPP_DWEB=A; EXP_AB_HLP_EDD=DEFAULT; EXP_CTA_DISABLE_DWEB=DEFAULT; EXP_AB_GETAPPNUDGE_MWEB=DEFAULT; EXP_AB_MWEB_FILTERS_PLP=A; EXP_AB_VISUAL_FILTERS_PLP=DEFAULT; EXP_AB_NYKAA_NOW_PDP=A; EXP_AB_CONVENIENCE_FEE=A; EXP_SPECIAL_DEALS=A; EXP_CONVERSATION_ROUTE=A; EXP_AB_FREE_GIFT=A; EXP_AB_SALE_PRICE_TAG=DEFAULT; EXP_MINI_COUPONS_OFFERS=A; EXP_AB_DS_AUTH_FLOW=A; EXP_DWEB_MINI_COUPONS_OFFERS=DEFAULT; EXP_AB_PRODUCT_RACK_CS=A; EXP_CART_STEP_COUNTER=DEFAULT; EXP_AB_RATING_REVIEW=A; EXP_AB_SHOW_ASPECTS=CONTROL; EXP_AB_SEARCHCOUNT_MWEB=B; EXP_AB_BOTTOM_NAV=A; EXP_AB_BP_DN_PERS=A; EXP_PLP_DESIGN_PARITY=A; EXP_AB_STICKY_PRICE_V2=A; EXP_PRODUCT_IMG_V2=A; EXP_AB_EDD_DESIGN_V2=A; EXP_CART_GROUPING=DEFAULT; EXP_DWEB_COLLAPSED_PRICE=A; EXP_COLLAPSED_PRICE_DETAILS=A; EXP_AB_HLP_AFFILIATE=DEFAULT; EXP_STORE_SUGGESTION=A; EXP_CART_SAVINGS_SHELF=A; EXP_CATEGORY_NUDGE=CONTROL; EXP_TOP_BRAND_FILTERS=A; EXP_CART_MINI_PDP=A; EXP_AB_AGG_FOOTER_SSR=CONTROL; EXP_MAP_PICKER=DEFAULT; EXP_COUPON_OFFER_REORDER=A; EXP_AB_PDP_LITE_OFFERS_SSR=CONTROL; EXP_HEADER_SUBSTORE_TABS=DEFAULT; EXP_VARIANT_SELECTOR_V2=CONTROL; EXP_LADDER_OFFERS=DEFAULT; EXP_AB_TOP_FILTERS_PLP=DEFAULT; EXP_FUTURE_COUPONS=DEFAULT; EXP_HLP_RECO_WIDGETS=C; EXP_UPDATED_AT=1783944471875; EXP_SSR_CACHE=adc40cbdb4941b708b07e44f17e465f4; bm_ss=ab8e18ef4e; bm_sz=EBC8B4E15EF84038DF43DD96AFE33DDF~YAAQLBzFF5V4f0ufAQAA8kL6XwDafBYwoq6RaLi1UtdUIvAVhFm1y5iW5Z0l1cxHR4yjCSEiCvzDQZPXjJ42ASq6wCNNa2UZpXsx1hHmrgxN/sYpNgQaD/IivRa7dFtNIe7IP8RNvLGNZU20iYH3KpW1E2F+w8JK02kH0hZA1NPyGTkl8X6EqX7V+7vXpzByq1DJQviCjkSMva/+rdGtAUT43X+tF6314daFl+NGdWwYiEkHqlRbzlOsGYxEGCOyXyVMObWC0GsL1NYaduZ7br+x4ug+ebDLxGXqMLP6/wKX/xA90gcaif2nbXNnpEJxxhflo9bhkAxX71DsOLMnYNmHiXk1gPGTCG4KPx9Lq687C3XgnFm3CvsTp1AOCIcx3w/wIY5CkCO87XSq4O4cuNlN/ZPP/0YfrVexUSzmgTrlBe9kWfMIpsd5ht408v2SDluDQSvFJOTV3Zv1VHCfvcsyg7kWwYUcHvIP52UnmouACGATTQ==~4535108~3355457; storeId=nykaa; bm_so=18058F2E87366C215CB80444EB80BEDC3F7B15F6C085A4B8D35EC98BC9DB7263~YAAQt0LHF0Wzo1OfAQAA9FIPYAhEaGZLNZBVKtaoW5QpBb8KB2ikQrsSfYBdeI84VRU9a8W3//z35luEJ25kFCn2V8tC5j3Sqx8Nyx25ts7+OMg0Tj2u/TBQgMhnRjgAkF4WvTrCcVEgcsYSqZtYtc0c1CfSy6KRvMwYAca8+FypvHOtV6akEEs0andyqXXF2RZMEPTHbquJ6VmhV5enWROzuEdjqmjeXH6eZmUuVpTxkamyg/t7z+tN8NjsMliA4j+wp5oY/S9z/jsKx+23YS0YxsdRHHcdlpBYQ87hq61kGBPcauZTtFdD+P2mPigpzwEEel7kBUMX0vTxMbiVm2XF2ccYRUM4Kgo/LULvWFZExQPky6kXC0VIgmipPTstdh+SLzOPo5ngTVVW0EONB9sA7IbpXVYZN8aO21VdcuXyJLxcW6moAn/8+v05uB6Huu68eNzTDEnNJ7SR+Pz2UANB6YD2; SITE_VISIT_COUNT=7; bm_s=YAAQt0LHF4C2o1OfAQAAs1kPYAVbvhoK2qwlldE/uDMnb+42VBxLofLn/ba4nLSCWusrLr8F0AnYk27hDkPr+1fUmrHLyfxHROWPyGaHAGWuTOMuQ1371UAJNGR/TK1e7+Swe991b1p0I09TezGMpYS3yazqytu2sfR7UbENUv75cMQQXuDVK71juBgBkXCR4H9fOrSvsjBPps9OmORH6XHElJl8llrnQy+F5o+mxaRuzUNXDqHQ269wfRXQqDw2GSx6F9P/RsVTRhRZu91D8mTI2Kj9McNMBir7uDPY68c/lwRhpCA18sdCI85Zx4eZQvdFWVZkDR7drxbp2saKrcyZc/0vbZtXHUWuHQETpm9+T5r6/hS/yqZTgTyU38L/YWrH4zA7Ym6M+tRP2BAA5JiHoEwZxdsXI9m73/uGJLcpDKSoHNtBC0RlKPUOGFKxsAilT9txWAygVvsa5ZPzYMEjU4cSKbf94uj1n5k51lIVup5NAIFcYuHYjWAT2S4Y6Z3aKmRrEE6dGH4cORhzDgObxAhB1d7c4Zsybt8qSqdNPhCwnt2GgcemZR+nODwO5Un9sErmFbfy6eqKUjkRCR3MhwqE3N66PlrcsuL8QCrt+d7DKNO9eeIhwp8hmJ82/W6k0ktCASlwc4NNGIb/6YAJ2r9aou3MY+sUdceDl8IXI3cVmHYStRlSqzhcLaAclPiPg0Rvyk9Fkph5XmKuAxuBGFqfzU4D7pfoOj0V7z6bIr/hhA4Qxp13TX4QwLCSkir5nlelllK7XfVB8E076sGol+gI+rKWXzqoBBTqllV0Eb39kZvrKlhSHYGB4JY/GDZlA4KG7IE2WMliqEX5Mtzbxk7Imdnf5RePXw2/xWwKFObhr/omErrWz3V+53IIU5ZwsHYBR0mk6g8yGDXdocAm3S6lKeaiL1DbdA8hGTl7Ofy6T/Jm+WOAjClK0VfqDR/oLGQ15WsS+eFkw/Qhhter4gbMH66g208=; bm_lso=18058F2E87366C215CB80444EB80BEDC3F7B15F6C085A4B8D35EC98BC9DB7263~YAAQt0LHF0Wzo1OfAQAA9FIPYAhEaGZLNZBVKtaoW5QpBb8KB2ikQrsSfYBdeI84VRU9a8W3//z35luEJ25kFCn2V8tC5j3Sqx8Nyx25ts7+OMg0Tj2u/TBQgMhnRjgAkF4WvTrCcVEgcsYSqZtYtc0c1CfSy6KRvMwYAca8+FypvHOtV6akEEs0andyqXXF2RZMEPTHbquJ6VmhV5enWROzuEdjqmjeXH6eZmUuVpTxkamyg/t7z+tN8NjsMliA4j+wp5oY/S9z/jsKx+23YS0YxsdRHHcdlpBYQ87hq61kGBPcauZTtFdD+P2mPigpzwEEel7kBUMX0vTxMbiVm2XF2ccYRUM4Kgo/LULvWFZExQPky6kXC0VIgmipPTstdh+SLzOPo5ngTVVW0EONB9sA7IbpXVYZN8aO21VdcuXyJLxcW6moAn/8+v05uB6Huu68eNzTDEnNJ7SR+Pz2UANB6YD2~1784023047906; _abck=7A6AA7CC7B049EA58E68B59D2F23BCEC~0~YAAQt0LHF5i7o1OfAQAATmcPYBBoY2blKiD/shZpCYrC9ZFlcSZEiTSh+JdjEB4Knto+i41jJgN33Smt6SmFTaeMTkjUt2Wph+IyuUl6S3ryVEIscAeAR1eC7lHlv8PdUm4CUBtVVFpFzziofZuzRktLMOzwhZLuN5qRp8omkY9eLMG21NL0gYVrxN1qPg3Yx/nzWLc4qSU/uQv+pyvLEVSazNE4PMD+xjpEgYs2yJdDYR+Hx9rk1RfuRpuTJW3nkHAwvO0b7hcv9m9QcWDIuC7rTeBHM7tXZ+4hQ5QeUXQ8uMIAm22fh2i5JZ6Gj9c+cfvB0Oy76PXwfRtE9fpEbfgTqz6YSrsvMtggzaSs+jVoL2dGOP/jWO8L3WkAWYfWN/qnPNsRtDkMwQRYRegCh+IiKRKKfC7G+7lfOKhXrxprYzUOU6hzneNta7K0moVtkIX4KhoMX1UXs4WZ6qtOVEkul8eC4KkQKFbtMlTN9++qBJWUPy54/diZinJIFEjRxbN9qXeufgpQ7unpmJI8GVUuLFfTTojwXHv5nbMNvvPzAyQvC/DPXruVirejeSEZmBHM9KfodYUOJTgyHQNHG5bgP0BKgmT4VTLum6gxUPwW6KfGDdWxSVcf6JtyMziBuzw9mEkDXouvT69lXZ2f7rOOOl6hGFQWwJLO5soKt0QVVhwLixG5gwSPR5RlC6e7weX6MwG3plunl3TaikHEJsEUWJ6rKEB77SxCNqU/hZTADYBmqct4jF1Dk+e90Xz5HbYQzu7mjmqHXhlIuHf2WoyB0yrPMbQD9A==~-1~-1~1784025757~AAQAAAAG%2f%2f%2f%2f%2f1qqbrVlLP7Hs0JCrExqY2FMgwGLKEckXGlc8asnyHiz8gxW9gCTti9rj64xgR8fVSIZD8lj5cECm50w19OF0BjFobbannuQMo6vtz2rPRvEuNsAzfU+ebUECMzw2DJDfw+kWhOqTIZseaEh5d1%2fnSqE9mLwCsso0ROs1SJ365jcR2PmXE7A6jPkohktTt+P6v4ndkX5+xjRAt2++w6IPh8fHLV6Pj+RL5yZ8dEzQRn5KvE%3d~-1; _uetsid=d14ba8307f4611f1a3c4ad39223b01a4; _uetvid=d14bca407f4611f1a69a4b36e992a3c8; _clsk=10gmm75%5E1784023051885%5E1%5E1%5El.clarity.ms%2Fcollect; cto_bundle=VDLGcl9neEtnVVk0Snd4ODF2bnUlMkYxY25IVFBQWkUlMkJPV1dKcEJjNkxpWll6a3RKd3hRcGVUdld5alMlMkJPaWhjYUxSMkdSdGhiVzRBNVNQVkpEbk56Wk9KT2Y3TXZQeWpEZDVLSjclMkYlMkIyYWFuMXZFZVZxWW1LR0tmVnJhSXdrdFlYclNnbkFIQVBhb2d0ZzRhZlZ6bXFwSVFGRmRRJTNEJTNE; _ga=GA1.2.651158749.1784007756; _gat_UA-31866293-9=1; _ga_JQ1CQHSXRX=GS2.2.s1784022572$o3$g1$t1784023055$j60$l0$h0; _ga_LKNEBVRZRG=GS2.1.s1784022573$o3$g1$t1784023057$j47$l0$h0; WZRK_S_656-WZ5-7K5Z=%7B%22p%22%3A5%2C%22s%22%3A1784022575%2C%22t%22%3A1784023058%7D; EXP_AB_AGG_FOOTER_SSR=CONTROL; EXP_AB_AUTH_DWEB=A; EXP_AB_AUTOFILL=B; EXP_AB_BEST_SELLER_PDP=A; EXP_AB_BOTTOM_NAV=A; EXP_AB_BP_DN_PERS=A; EXP_AB_CAB_VERTICAL=DEFAULT; EXP_AB_CALLOUT_NUDGE=A; EXP_AB_CART_OFFERS=A; EXP_AB_CONVENIENCE_FEE=A; EXP_AB_CP_GAMES=A; EXP_AB_DS_AUTH_FLOW=A; EXP_AB_DWEB_MULTICOUPON=A; EXP_AB_DWEB_SHOPPING_BAG_URL=A; EXP_AB_EDD_DESIGN_V2=A; EXP_AB_EMAIL_VERIFICATION_REVAMP=A; EXP_AB_ENABLE_HLP_NEW_API=DEFAULT; EXP_AB_FREE_GIFT=A; EXP_AB_GETAPPNUDGE_MWEB=DEFAULT; EXP_AB_GETAPP_DWEB=A; EXP_AB_GOOGLE_ONE_TAP=DEFAULT; EXP_AB_HLP_AFFILIATE=DEFAULT; EXP_AB_HLP_CARD_REVAMP=CONTROL; EXP_AB_HLP_EDD=DEFAULT; EXP_AB_HLP_OFFERS=DEFAULT; EXP_AB_HLP_PAGE=A; EXP_AB_HORIZONTAL_WIDGET_TYPE=CONTROL; EXP_AB_HP_SEARCH_ANIMATION=CONTROL; EXP_AB_IOC_CART_NUDGE=DEFAULT; EXP_AB_MWEB_FILTERS_PLP=A; EXP_AB_NEW_GC_PAGE=A; EXP_AB_NEW_SHOPPING_BAG=A; EXP_AB_NEW_TAGS_ON_PDP=A; EXP_AB_NYKAA_NOW_CART=A; EXP_AB_NYKAA_NOW_FILTER=DEFAULT; EXP_AB_NYKAA_NOW_PDP=A; EXP_AB_NYKAA_NOW_RAAP=A; EXP_AB_OFFER_DELTA_COMMUNICATION=A; EXP_AB_PARTIAL_CHECKOUT=A; EXP_AB_PDP_HAMBURGER=CONTROL; EXP_AB_PDP_IMAGE=DEFAULT; EXP_AB_PDP_LITE_OFFERS_SSR=CONTROL; EXP_AB_PDP_SIMILAR_PRODUCT_SHEET=DEFAULT; EXP_AB_PRICE_REVEAL_NEW=A; EXP_AB_PRODUCT_RACK_CS=A; EXP_AB_RATING_REVIEW=A; EXP_AB_REMOVE_LOGIN_BOTTOMSHEET=DEFAULT; EXP_AB_SALE_PRICE_TAG=DEFAULT; EXP_AB_SAVINGS_SHELF=DEFAULT; EXP_AB_SEARCHCOUNT_MWEB=B; EXP_AB_SHOW_ASPECTS=CONTROL; EXP_AB_SIZE_MINI_PRODUCT=A; EXP_AB_STICKY_PRICE_V2=A; EXP_AB_TAGS_RATING_ON_LISTING=ONLY_TAGS; EXP_AB_TOP_FILTERS_PLP=DEFAULT; EXP_AB_TOP_NAV_CONFIG=CONTROL; EXP_AB_TRUECALLER=DEFAULT; EXP_AB_VISUAL_FILTERS_PLP=DEFAULT; EXP_AB_WEB_AUTOREAD_OTP=DEFAULT; EXP_AB_WISHLIST=A; EXP_AB_ZENDESK_CHAT=A; EXP_ADP_RV_MULTI_COUPONS=A; EXP_ADP_RV_PRODUCT_V3=CONTROL; EXP_ADP_RV_REORDER=B; EXP_ADP_RV_SEARCH_BAR_NEW=A; EXP_ADP_RV_SEGMENT=A; EXP_ADP_RV_VIEW_SIMILAR=A; EXP_ADP_RV_VIEW_SIMILAR_HLP=A; EXP_AD_BRV=random; EXP_APPSFLYER_DOWNLOAD_CTA=DEFAULT; EXP_CART_GRATIFICATION_POPUP=B; EXP_CART_GROUPING=DEFAULT; EXP_CART_LOGIN_SEGMENT=A; EXP_CART_MINI_PDP=A; EXP_CART_SAVINGS_SHELF=A; EXP_CART_STEP_COUNTER=DEFAULT; EXP_CATEGORY_NUDGE=CONTROL; EXP_COLLAPSED_PRICE_DETAILS=A; EXP_CONVERSATION_ROUTE=A; EXP_COUPON_OFFER_REORDER=A; EXP_CTA_DISABLE_DWEB=DEFAULT; EXP_C_W_P_M=1; EXP_DWEB_COLLAPSED_PRICE=A; EXP_DWEB_MINI_COUPONS_OFFERS=DEFAULT; EXP_EDD_DELIVERY_WIDGET=A; EXP_ERROR_BOUNDARY=DEFAULT; EXP_FULL_SCREEN_RECO_WIDGET=DEFAULT; EXP_FUTURE_COUPONS=DEFAULT; EXP_HEADER_SUBSTORE_TABS=DEFAULT; EXP_HLP_RECO_WIDGETS=C; EXP_H_F_M_M_S_P=1; EXP_H_F_M_P_S=1; EXP_H_F_M_S=1; EXP_H_F_M_W=1; EXP_ITEM_DISCOUNT=A; EXP_LADDER_OFFERS=DEFAULT; EXP_MAP_PICKER=DEFAULT; EXP_MINI_COUPONS_OFFERS=A; EXP_NEW_SIGN_UP=DEFAULT; EXP_OL=DEFAULT; EXP_ORDERS_REVAMP=A; EXP_PDP_RELEVANT_CATEGORY=DEFAULT; EXP_PLP_DESIGN_PARITY=A; EXP_PLP_DNW_DWEB=A; EXP_PLP_INLINE_FILTER=REVAMPED; EXP_PLP_INLINE_WIDGETS=A; EXP_PLP_PINKBOX_CTA=CONTROL; EXP_PRIVE_CTA_DISABLE=DEFAULT; EXP_PRODUCT_IMG_V2=A; EXP_QUERY_PARAM_EXP=C; EXP_QUERY_PARAM_EXP_DWEB=CONTROL; EXP_REVIEW_COLLECTION=1; EXP_REVIEW_SUBMIT=A; EXP_SEARCH_INP_ON_CART=A; EXP_SPECIAL_DEALS=A; EXP_SPECULATIVE_PRERENDERING=CONTROL; EXP_SSR_CACHE=adc40cbdb4941b708b07e44f17e465f4; EXP_STORE_SUGGESTION=A; EXP_TOP_BRAND_FILTERS=A; EXP_UPDATED_AT=1783944471875; EXP_VARIANT_SELECTOR_V2=CONTROL; _abck=7A6AA7CC7B049EA58E68B59D2F23BCEC~-1~YAAQDqTBF81DJUqfAQAAHI0WYBC2S3gyTzUgeTI32AdOLeYGk38B0//oCreCZFsDAXuD6/3edVX9egMYk1IyxRZZvr4q6s3beOJgPKpvqRSa8eNmm8qx79i5w+uUO/qZXYICbrParlHxOuAFMImUKamM0o3gcUGUcXrHnAwBT/DyDBKh8koLHa5WQlLX1/yHyFwyxmi6N02Vlaje094/uXLRgi/7rQ2bP24tSW/3cEcDaWrpp+EbUJZTfe7EARwZQDxzxokvv7cxjBh2vXoJFiK1QB51KDwirjpqAhffb5jXs+0VOkE+f4ymPXPmfKPm2WpAPHKkyKVNbXJgIP9QFghoZwjvXCsdiFf7Si02yTyRLhLgXJYs6TCC1w2jdv4WZ4hfEM04kfMwJZMJHcr0FrEeskrfie8lncBOzsi4VvXAETFNkfdNhjnIU1p3jbeGVXOaPqRTmUxnDnFupADFuO/nL+fKnglH9RGCxJlwmXVLeTs6LT+4ik2CIYZxA/vDh99CRZgM79+ZYFs8iGl7AOsf4ip1LBXw7wQBVW3u2CGBBfWwZFh+SPBceXOoW+K1FFG6Y4I/x8PNFYPwH9HqEf2mXDkqTK/hprFd2Vq8naXSk2GFfbjPoX1HhHpfvKS3znDcX/nT6j7gGAkT212w1TmIIPJfYGTpQ3ElDGCBL9fnaSpctRbPlcmHJP9/cS4nNlML1P694rHyJx+cDC7Yj0FAo6mf00eXuV/s5uQWF73MXluzD4g0+p7y45Xj8HMOao1ymCtdy0nzXtYI6bYhWTmljnz6Ot3F1A==~0~-1~1784025757~AAQAAAAG%2f%2f%2f%2f%2f1qqbrVlLP7Hs0JCrExqY2FMgwGLKEckXGlc8asnyHiz8gxW9gCTti9rj64xgR8fVSIZD8lj5cECm50w19OF0BjFobbannuQMo6vtz2rPRvEuNsAzfU+ebUECMzw2DJDfw+kWhOqTIZseaEh5d1%2fnSqE9mLwCsso0ROs1SJ365jcR2PmXE7A6jPkohktTt+P6v4ndkX5+xjRAt2++w6IPh8fHLV6Pj+RL5yZ8dEzQRn5KvE%3d~-1; bcookie=d62314e2-1f7f-4fbb-b370-ea861a643340; bm_s=YAAQDqTBF85DJUqfAQAAHI0WYAXbXOLqTgxNpPerXpAxVCYe6b5Xh3TcjvuPXBY6Tw3W3abhkQu1wbER5J35r7y0Ebn/C/iAbrozMd069OB2pleTmqawGT7jIypK4oiTxu66b3tHTtSNIUkFm1BuksWI/D6KS8WKRIoLTliecs6NgkZBVWtYB3mxEVyBpARs7td0UciA64dh/appRoEoZb0ivCdCoG53FbtGsrN25WAyQbAa5btByj5jTIFfPD+V0aChYzYTS/etW8LAU/Uz+dBgH9PLzs8yfRTljxI6cprV7XGwvH2atv0MHEJzFQQbOCiNxQ/apu1mCGxaP2+FWTrxHA1m3/Mir8hQdyOWyxK/wccN1Yk0xb2BXtnrpK49TDoI2F1q0zYRh21Ud1LkwHEojUNla4Wx5fO90ZpmUbC1+3AhyE7e2MgTKAnFh0Nb56z9xpz2Gpl0Y4fqNSvgGaR1UrHA3kSak84POHKXSTqrMWoJLRTT3iCkMy8FONO6A4ERR5RKwdbw8xKtNhQH1F29xG+DlZ5zYcESCK4atgY7wf//+TWGz8JQHS8Q7gLoHXd4XD7XvqTEyFpFnJ+BNc6MWcMO0Wyozgov8QPCz1nvcgMtj55WPbt3xNEbSNT1reXW18z3sClyK2aKsuHR6dJtD5UqQajdcD5lUoo7i/sIqpTvYBEGJly5gVL8koex4z3NUwPTYioxFBY=; bm_so=62EB724CB80E844A87F3EB3D52E1448B66BB29F2B5B36ADB74A085A038AFD053~YAAQt/Q3F2Cv/ECfAQAAzcwnXwjzPk9rmU5ikfoJiO+mmK0SBHViapHXhoUK+T3gmBAcRJIETpPzArgWuzc3LVmCIykm7Q8P4tevUoMruCMCFD/5AoLkHjNGql9VsmnbYGOYMjriuPCsjqPzQVsu4Ij+VLFzwn0/Fbb79U3tgzCkdVp9D8/VbG/hHzD/JH/KoJIE5eoOR2jgU9VWZKGKA/EGx4d+N7LWKgJRFFqoEwlC+5eEsKv2FzBTkCG8LdygtgJEATYHA1TugdO2OLoAZf6wA4/tB/UWF58syWrH7CJ7X3Y+WX6jpUTfB4PBAgh0kb9AqRhwahaANpH0SAgJNI1nPI32uz2HJDz+msiVfrJeoyfBrSGZleymccAZKCA6QnL4eImdOoBOs+FJsmLQtSM1yXfDz+EMolaPar1ORSQFDKLFC1dxnnaGjDxvPvT1O66dSOJ2QvhZVKjUI9cL98fnS74k; storeId=nykaa',
}


def fetch_page(category_id, page_no, session):
    params = {"category_id": category_id, "page_no": page_no}
    resp = session.get(API_URL, params=params, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.json()


def find_first(data, keys):
    """Recursively search a nested dict/list for the first matching key."""
    if isinstance(data, dict):
        for k in keys:
            if k in data:
                return data[k]
        for v in data.values():
            result = find_first(v, keys)
            if result is not None:
                return result
    elif isinstance(data, list):
        for item in data:
            result = find_first(item, keys)
            if result is not None:
                return result
    return None


def extract_pagination_info(data):
    total_found = data.get("total_found")
    product_count = data.get("product_count")
    return total_found, product_count


def extract_raw_products(data):
    return find_first(data, ["products"]) or []


def parse_products(product_data):
    products = []
    for product in product_data or []:
        try:
            sale = product.get("cohortSaleTemplate") or {}
            products.append(
                {
                    "product_id": product.get("productId", ""),
                    "sku": product.get("sku", ""),
                    "slug": base_url + product.get("slug", ""),
                    "product_name": product.get("productTitle", ""),
                    "brand_name": product.get("brandName", ""),
                    "price": product.get("price", 0),
                    "original_price": product.get("mrp", 0),
                    "offer": product.get("offer", ""),
                    "image_url": product.get("imageUrl", ""),
                    "in_stock": product.get("inStock", False),
                    "rating": product.get("rating", 0),
                    "rating_count": product.get("ratingCount", 0),
                    "quantity": product.get("quantity", 0),
                    "discount": product.get("discount", 0),
                    "new_tags": [
                        tag.get("title", "") for tag in (product.get("newTags") or [])
                    ],
                    "sale": {
                        "sale_price": sale.get("price", 0),
                        "text": sale.get("text", ""),
                        "sale_discount": sale.get("discount", 0),
                    },
                    "most_reordered": bool(product.get("secondaryTag")),
                }
            )
        except Exception:
            continue
    return products


def scrape_category(category_id, output_dir):
    session = requests.Session()
    all_products = []

    print(f"Fetching page 1 for category_id={category_id} ...")
    first_page = fetch_page(category_id, 1, session)

    total_found, product_count = extract_pagination_info(first_page)

    if not total_found or not product_count:
        print("⚠️  Could not auto-detect totalFound/count.")
        print("Top-level keys in response:", list(first_page.keys()))
        print("Paste that structure back to me and I'll wire up the exact field names.")
        return

    total_pages = -(-total_found // product_count)  
    print(
        f"total_found={total_found}, product_count={product_count}, total_pages={total_pages}\n"
    )

    all_products.extend(parse_products(extract_raw_products(first_page)))
    print(f"  Page 1/{total_pages}: {len(all_products)} product(s) so far")

    for page_no in range(2, total_pages + 1):
        time.sleep(1)  
        page_data = fetch_page(category_id, page_no, session)
        page_products = parse_products(extract_raw_products(page_data))
        all_products.extend(page_products)
        print(
            f"  Page {page_no}/{total_pages}: +{len(page_products)} (total {len(all_products)})"
        )

    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"category_{category_id}.json"
    output_file.write_text(
        json.dumps(all_products, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\n✅ Done. Saved {len(all_products)} product(s) to {output_file}")


def main():
    category_id = input("Enter category_id: ").strip()
    output_dir = Path("output_data")
    scrape_category(category_id, output_dir)


if __name__ == "__main__":
    main()
