import os
import random
import requests
import asyncpg
import csv
from dotenv import load_dotenv
from discord import Intents, Client, Interaction, Embed, Colour
from discord.ext import commands, tasks
from autokattis import OpenKattis
from datetime import datetime, timedelta, time

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')

intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

GITHUB_REPO_URL = 'https://github.com/kashsuks/DSABot'

ALGORITHMS = [
    "Binary Search", 
    "Stacks",
    "Linked-List",
    "Breadth-First-Search (BFS)",
    "Depth-First-Search (DFS)",
    "Djikstra's Algorithm",
    "Floyd Warshall's Algorithm",
    "Prim's Algorithm",
    "Kruskal's Algorithm",
    "Longest Common Subsequence",
    "Longest Increasing Subsequence",
    "Edit Distance",
    "Minimum Partition",
    "Ways to Cover a Distance",
    "Quick Sort",
    "Merge Sort",
    "KMP Algorithm",
    "Z's Algorithm",
    "Sieve of Eratosthenes",
    "Tries",
    "Backtracking",
    "Binary Search Tree",
    "Chinese Remainder Theorem",
    "Queue (FIFO)",
    "Permutations",
    "Recursion",
    "Dynamic Programming",
    "Backtracking",
    "0 1 Knapsack Problem",
    "Graph Theory"
]

async def init_db():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS user_handles (
            id SERIAL PRIMARY KEY,
            discord_id BIGINT UNIQUE NOT NULL,
            codeforces_handle TEXT UNIQUE NOT NULL,
            rating INT NOT NULL
        )
    """)
    await conn.close()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.tree.sync()
    await init_db()
    print("Database initialized.")
    
@bot.tree.command(name="repo", description="Send the link to my GitHub repository")
async def repo(interaction: Interaction):
    await interaction.response.send_message(f"Here is the link to my GitHub repo: {GITHUB_REPO_URL}")

@bot.tree.command(name="random-algo", description="Get a random algorithm to learn")
async def random_algo(interaction: Interaction):
    algorithm = random.choice(ALGORITHMS)
    await interaction.response.send_message(f"Learn about this algorithm: {algorithm}")

@bot.tree.command(name="resources", description="Resources used to learn competitive programming")
async def resources(interaction: Interaction):
    await interaction.response.send_message(f"Here are some competitive programming resources:\n https://cp-algorithms.com/index.html \n https://xlinux.nist.gov/dads/ \n https://leetcode.com/ \n https://codeforces.com/ \n https://open.kattis.com/")

@bot.tree.command(name="random-problem", description="Gives a random problem from Kattis")
async def random_problem(interaction: Interaction):
    await interaction.response.defer()
    try:
        kt = OpenKattis(os.getenv('KATTIS_USERNAME'), os.getenv('KATTIS_PASSWORD'))
        problems = kt.suggest()
        if not problems:
            await interaction.followup.send("No problems found. Please try again later.")
            return

        problem = random.choice(problems)
        name = problem.get('name', 'Unknown')
        difficulty = problem.get('difficulty', 'Unknown')
        link = problem.get('link', 'No link available')

        await interaction.followup.send(f"Here is a Kattis problem for you to try:\n**Name:** {name}\n**Difficulty:** {difficulty}\n**Link:** {link}")
    except Exception as e:
        await interaction.followup.send("An error occurred while fetching a problem from Kattis.")
        print(e)

@bot.tree.command(name="set-handle-cf", description="Set your Codeforces handle to get rating information")
async def set_handle_cf(interaction: Interaction, username: str):
    url = f"https://codeforces.com/api/user.rating?handle={username}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        if data['status'] == 'OK' and data['result']:
            latestRating = data['result'][-1]
            newRating = latestRating['newRating']
            discord_id = interaction.user.id

            try:
                conn = await asyncpg.connect(DATABASE_URL)
                await conn.execute("""
                    INSERT INTO user_handles (discord_id, codeforces_handle, rating)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (discord_id) DO UPDATE
                    SET codeforces_handle = $2, rating = $3
                """, discord_id, username, newRating)
                await conn.close()

                await interaction.response.send_message(f"Your Codeforces rating has been saved. Current rating for {username}: {newRating}")
            except Exception as e:
                await interaction.response.send_message(f"An error occurred while saving your data: {e}")
        else:
            await interaction.response.send_message(f"No rating data found for {username}. Please check your handle and try again.")
    else:
        await interaction.response.send_message(f"Error fetching data for {username}. Please try again later.")
        
@bot.tree.command(name="set-handle-lc", description="Set your Leetcode handle to get rating information")
async def set_handle_lc(interaction: Interaction, username: str):
    
    url = f"https://alfa-leetcode-api.onrender.com/{username}/contest"
        
@bot.tree.command(name="leaderboard", description="Show the top 10 Codeforces users in the server")
async def leaderboard(interaction: Interaction):
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        rows = await conn.fetch("""
            SELECT discord_id, codeforces_handle, rating 
            FROM user_handles 
            ORDER BY rating DESC
        """)
        await conn.close()
        
        leaderboardEmbed = Embed(
            title="Codeforces Leaderboard",
            color=Colour.red()
        )
        description = ""

        for i, row in enumerate(rows[:10], start=1):
            description += f"**#{i}** {row['codeforces_handle']} --> {row['rating']}\n"

        leaderboardEmbed.description = description

        userRank = None
        for i, row in enumerate(rows, start=1):
            if row['discord_id'] == interaction.user.id:
                userRank = i
                break

        if userRank:
            leaderboardEmbed.add_field(
                name="Your Rank",
                value=f"**#{userRank}** {interaction.user.mention}",
                inline=False
            )
        else:
            leaderboardEmbed.add_field(
                name="Your Rank",
                value="You are not on the leaderboard.",
                inline=False
            )

        await interaction.response.send_message(embed=leaderboardEmbed)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred while fetching the leaderboard: {e}")
            
#Role specific commands

@bot.tree.command(name="update-rating", description="Update all Codeforces rating and list all changes.")
async def update_rating(interaction: Interaction):
    if "Kashyap" not in [role.name for role in interaction.user.roles]: # Replace `Kashyap` with whatever role your admin has, whether that be `Admin` or something else.
        await interaction.response.send_message("You do not have permissions to send this command.")
        return
    
    await interaction.response.defer()
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        rows = await conn.fetch("SELECT id, codeforces_handle, rating FROM user_handles")
        
        ratingChanges = []
        for row in rows:
            handle = row['codeforces_handle']
            oldRating = row['rating']
            
            url = f"https://codeforces.com/api/user.rating?handle={handle}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'OK' and data['result']:
                    latestRating = data['result'][-1]['newRating']
                    
                    if latestRating != oldRating:
                        ratingChange = latestRating - oldRating
                        ratingChanges.append(f"**{handle}:** {oldRating} --> {ratingChange:+} --> {latestRating}")
                        
                        await conn.execute("""
                            UPDATE user_handles
                            SET rating = $1
                            WHERE id = $2
                        """, latestRating, row['id'])
            
            else:
                print(f"Failed to fetch rating for {handle}")
        
        await conn.close()
        
        embed = Embed(
            title="Codeforces Rating Updates",
            color=Colour.red()
        )

        if ratingChanges:
            embed.description = "\n".join(ratingChanges)
        else:
            embed.description = "**No rating changes**"

        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send("An error occurred while updating the ratings.")
        print(e)

@bot.tree.command(name="save-database", description="Save the entire database data to a CSV for easy instance-hopping")
async def save_database(interaction: Interaction):
    if "Kashyap" not in [role.name for role in interaction.user.roles]:
        await interaction.response.send_message("You do not have permissions to run this command.")
        return

    await interaction.response.defer()
    
    try:
        directory = "local_saves"
        os.makedirs(directory, exist_ok=True)
        
        conn = await asyncpg.connect(DATABASE_URL)
        rows = await conn.fetch("SELECT * FROM user_handles")
        await conn.close()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filePath = os.path.join(directory, f"user_handles_{timestamp}.csv")
        
        with open(filePath, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            if rows:
                writer.writerow(rows[0].keys())
                
            for row in rows:
                writer.writerow(row.values())
        
        await interaction.followup.send(f"Database data has been saved to `{filePath}`.")
        
    except Exception as e:
        await interaction.followup.send("An error occured while copying data.")
        print(e)

bot.run(TOKEN)