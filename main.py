import os 
import random
from dotenv import load_dotenv
from discord import Intents, Client, Interaction
from discord.ext import commands
import requests

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

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

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.tree.sync()

@bot.tree.command(name="repo", description="Send the link to my GitHub repository")
async def repo(interaction: Interaction):
    await interaction.response.send_message(f"Here is the link to my GitHub repo: {GITHUB_REPO_URL}")
    
@bot.tree.command(name="random-algo", description="Get a random algorithm to learn")
async def random_algo(interaction: Interaction):
    algorithm = random.choice(ALGORITHMS)
    await interaction.response.send_message(f"Learn about this algorithm: {algorithm}")
    
@bot.tree.command(name="resources", description="Resources used to learn competitve programming")
async def resources(interaction: Interaction):
    await interaction.response.send_message(f"Here are some competitive programming resources:\n https://cp-algorithms.com/index.html \n https://xlinux.nist.gov/dads/")

bot.run(TOKEN)