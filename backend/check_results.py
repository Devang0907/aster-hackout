import asyncio
from app.core.database import get_database

async def check():
    db = await get_database()
    factory_id = "5e35ef1a-d49c-4f0a-8dbd-dc3bcc286bbc"
    
    # Check carbon results
    results = await db.carbonresult.find_many(where={'factoryId': factory_id})
    print(f'Carbon results for factory {factory_id}: {len(results)}')
    for r in results:
        print(f'  - ID: {r.id}, netCo2e: {r.netCo2e}')
    
    # Check reporting periods
    periods = await db.reportingperiod.find_many(where={'factoryId': factory_id})
    print(f'\nReporting periods: {len(periods)}')
    for p in periods:
        print(f'  - ID: {p.id}, status: {p.status}, period: {p.periodStart} to {p.periodEnd}')

asyncio.run(check())
