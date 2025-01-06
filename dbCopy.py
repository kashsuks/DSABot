import os
import csv
import asyncpg
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

async def CSVtoDB():
    try:
        directory = 'local_saves'
        csvFile = [f for f in os.listdir(directory) if f.endswith('.csv')]
        if not csvFile:
            print("No csv files found in the directory")
            return
        
        latest_file = max(
            [os.path.join(directory, f) for f in csvFile],
            key=os.path.getctime
        )
        
        print(f"Importing data from {latest_file}")
        
        conn = await asyncpg.connect(DATABASE_URL)
        
        with open(latest_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            async with conn.transaction():
                for row in reader:
                    await conn.execute("""
                        INSERT INTO user_handles (discord_id, codeforces_handle, rating)
                        VALUES ($1, $2, $3)
                        ON CONFLICT (discord_id) DO UPDATE
                        SET codeforces_handle = $2, rating = $3
                    """, int(row['discord_id']), row['codeforces_handle'], int(row['rating']))

        await conn.close()
        print("Data import completed successfully.")
        
    except Exception as e:
        print(f"An error occurred: {e}")

CSVtoDB()