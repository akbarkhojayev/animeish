#!/usr/bin/env python3
"""
Dashboard test script
"""
import os
import sys
import django

# Django settings ni yuklash
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Dashboard callback ni test qilish
try:
    from main.dashboard import dashboard_callback
    from django.test import RequestFactory

    print("🔍 Dashboard callback test boshlanmoqda...")

    # Fake request yaratish
    factory = RequestFactory()
    request = factory.get('/admin/')

    # Bo'sh context yaratish
    context = {}

    # Callback ni chaqirish
    result_context = dashboard_callback(request, context)

    print("\n📊 Dashboard statistikasi:")
    print(f"✅ Jami filmlar: {result_context.get('total_movies', 'Noma\'lum')}")
    print(f"✅ Jami foydalanuvchilar: {result_context.get('total_users', 'Noma\'lum')}")
    print(f"✅ Jami epizodlar: {result_context.get('total_episodes', 'Noma\'lum')}")
    print(f"✅ Jami janrlar: {result_context.get('total_genres', 'Noma\'lum')}")
    print(f"✅ So'nggi 30 kun filmlar: {result_context.get('recent_movies', 'Noma\'lum')}")
    print(f"✅ O'rtacha reyting: {result_context.get('avg_rating', 'Noma\'lum')}")

    print(f"\n📋 Top filmlar soni: {len(result_context.get('top_movies', []))}")
    print(f"📋 Top janrlar soni: {len(result_context.get('top_genres', []))}")

    print("\n🎉 Dashboard callback muvaffaqiyatli ishlamoqda!")

except Exception as e:
    print(f"❌ Xatolik: {e}")
    import traceback
    traceback.print_exc()
