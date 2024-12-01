from aiohttp import web
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from db import get_db
from models import User, Stats

async def create_user(request):
    data = await request.json()
    telegram_id = data.get('telegram_id')
    username = data.get('username')
    
    if not telegram_id:
        return web.json_response({"error": "telegram_id is required"}, status=400)
        
    async with get_db() as session:
        # Check if user exists
        query = select(User).filter(User.telegram_id == telegram_id)
        result = await session.execute(query)
        user = result.scalar()
        
        if not user:
            # Create new user
            user = User(telegram_id=telegram_id, username=username)
            session.add(user)
            await session.commit()
            
            # Create initial stats
            stats = Stats(user=user)
            session.add(stats)
            await session.commit()
        
        return web.json_response({
            "id": user.id,
            "telegram_id": user.telegram_id,
            "username": user.username,
            "level": user.level,
            "account_status": user.account_status
        })

async def get_user_stats(request):
    telegram_id = request.query.get('telegram_id')
    if not telegram_id:
        return web.json_response({"error": "telegram_id is required"}, status=400)
    
    async with get_db() as session:
        # Try to find or create user
        query = select(User).filter(User.telegram_id == telegram_id)
        result = await session.execute(query)
        user = result.scalar()
        
        if not user:
            # Create new user and stats
            user = User(telegram_id=telegram_id)
            session.add(user)
            await session.commit()
            
            stats = Stats(user=user)
            session.add(stats)
            await session.commit()
        else:
            # Get existing stats
            query = (
                select(User, Stats)
                .outerjoin(Stats, Stats.user_id == User.id)
                .filter(User.telegram_id == telegram_id)
            )
            result = await session.execute(query)
            row = result.first()
            if row:
                user, stats = row
            else:
                stats = Stats(user=user)
                session.add(stats)
                await session.commit()
                
        # Count qualified referrals (users who reached level 5)
        referral_count = user.referral_count
        
        response = {
            "talk_time": {
                "today": stats.talk_time_today if stats else 0,
                "weekly": stats.talk_time_weekly if stats else 0,
                "total": stats.talk_time_total if stats else 0
            },
            "listened_time": stats.listened_time if stats else 0,
            "days_engaged": stats.days_engaged if stats else 0,
            "invited_friends": referral_count,
            "level": user.level,
            "account_status": user.account_status
        }
        return web.json_response(response)

async def get_user_profile(request):
    telegram_id = request.query.get('telegram_id')
    if not telegram_id:
        return web.json_response({"error": "telegram_id is required"}, status=400)
        
    async with get_db() as session:
        query = select(User).filter(User.telegram_id == telegram_id)
        result = await session.execute(query)
        user = result.scalar()
        
        if not user:
            # Create new user
            user = User(telegram_id=telegram_id)
            session.add(user)
            await session.commit()
            
            # Create initial stats
            stats = Stats(user=user)
            session.add(stats)
            await session.commit()
            
        profile = {
            "name": user.username or "Student",
            "avatar": "/static/image/student_avatar.png"
        }
        return web.json_response(profile)

async def track_referral(request):
    data = await request.json()
    referrer_id = data.get('referrer_id')
    referee_id = data.get('referee_id')
    
    if not all([referrer_id, referee_id]):
        return web.json_response({"error": "Both referrer_id and referee_id are required"}, status=400)
        
    async with get_db() as session:
        # Check if referee already exists
        query = select(User).filter(User.telegram_id == referee_id)
        result = await session.execute(query)
        existing_user = result.scalar()
        if existing_user:
            if existing_user.referred_by:
                return web.json_response({
                    "error": "User already registered through another referral",
                    "referral_count": existing_user.referral_count
                }, status=400)
            return web.json_response({
                "error": "User already registered",
                "referral_count": existing_user.referral_count
            }, status=400)
            
        # Get referrer
        query = select(User).filter(User.telegram_id == referrer_id)
        result = await session.execute(query)
        referrer = result.scalar()
        
        if not referrer:
            return web.json_response({"error": "Referrer not found"}, status=404)
            
        # Create new user with referral
        new_user = User(
            telegram_id=referee_id,
            referred_by=referrer.id
        )
        session.add(new_user)
        
        # Create initial stats for the new user
        new_stats = Stats(user=new_user)
        session.add(new_stats)
        
        await session.commit()
        
        # Check if referrer gets premium
        if referrer.referral_count >= 10:
            referrer.account_status = 'PREMIUM'
            await session.commit()
            
        return web.json_response({
            "success": True,
            "referral_count": referrer.referral_count,
            "premium_earned": referrer.account_status == 'PREMIUM'
        })

def setup_routes(app, cors):
    # Add CORS to routes
    app.router.add_route("GET", "/api/stats", get_user_stats)
    app.router.add_route("GET", "/api/profile", get_user_profile)
    app.router.add_route("POST", "/api/referral", track_referral)
    app.router.add_route("POST", "/api/users", create_user)
    
    # Configure CORS for all routes
    for route in list(app.router.routes()):
        cors.add(route)
