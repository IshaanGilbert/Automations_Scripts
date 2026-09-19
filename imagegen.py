# import cv2
# import numpy as np
# import os
# from random import randint, uniform

# save_folder = "green_circles"
# os.makedirs(save_folder, exist_ok=True)

# for i in range(1000000):  # 10 लाख images
#     # 256x256 या 512x512 size image banao
#     img = np.ones((256, 256, 3), dtype=np.uint8) * 255  # white background
    
#     # random green shade
#     green_shade = (randint(80, 255), randint(140, 255), randint(30, 120))
    
#     # random circle position & size
#     center_x = randint(40, 216)
#     center_y = randint(40, 216)
#     radius = randint(30, 100)
    
#     # draw circle (filled ya border दोनों try kar sakte ho)
#     cv2.circle(img, (center_x, center_y), radius, green_shade, -1)  # -1 = filled
    
#     # थोड़ा noise / variation डाल सकते हो
#     if randint(0, 10) > 7:
#         img = cv2.GaussianBlur(img, (5,5), 0)
    
#     cv2.imwrite(f"{save_folder}/green_circle_{i:07d}.jpg", img)




# import cv2
# import numpy as np
# import os
# from random import randint, choice, uniform 

# save_folder = "green_realistic_objects"
# os.makedirs(save_folder, exist_ok=True)

# object_types = ['apple', 'ball', 'lime', 'orange']  # Alag alag types

# for i in range(10):  # 10 लाख
#     size = randint(256, 512)
#     img = np.ones((size, size, 3), np.uint8) * 255  # White bg
    
#     obj_type = choice(object_types)  # Random type choose
    
#     # Base color green shades (type ke hisab se vary)
#     if obj_type == 'apple':
#         color = (randint(50, 100), randint(150, 200), randint(100, 150))  # Shiny green apple
#     elif obj_type == 'ball':
#         color = (randint(20, 60), randint(180, 220), randint(80, 120))  # Tennis ball green
#     elif obj_type == 'lime':
#         color = (randint(30, 70), randint(200, 255), randint(50, 100))  # Bright lime
#     else:  # orange (unripe green)
#         color = (randint(40, 80), randint(160, 210), randint(120, 160))  # Greenish orange tint
    
#     center = (size//2 + randint(-50,50), size//2 + randint(-50,50))
#     radius = randint(int(size*0.3), int(size*0.45))
    
#     # Main body (slightly oval for realism)
#     cv2.ellipse(img, center, (radius, int(radius * uniform(0.9, 1.1))), 0, 0, 360, color, -1)
    
#     # 3D shading: highlight + shadow
#     highlight_pos = (center[0] - radius//4, center[1] - radius//4)
#     shadow_pos = (center[0] + radius//4, center[1] + radius//4)
#     highlight_color = (min(255, color[0]+50), min(255, color[1]+40), min(255, color[2]+30))
#     shadow_color = (max(0, color[0]-50), max(0, color[1]-40), max(0, color[2]-30))
#     cv2.circle(img, highlight_pos, radius//2, highlight_color, -1)
#     cv2.circle(img, shadow_pos, radius//2, shadow_color, -1)
    
#     # Texture: noise for skin/fuzz
#     if obj_type in ['apple', 'lime', 'orange']:
#         noise = np.random.normal(0, 15, img.shape).astype(np.int16)  # Fruit skin bumps
#     else:  # ball
#         noise = np.random.normal(0, 5, img.shape).astype(np.int16)  # Fuzzy tennis ball
#     img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
#     # Extra features per type
#     if obj_type in ['apple', 'lime', 'orange']:
#         # Stem/leaf
#         stem_color = (randint(50,100), randint(100,150), randint(20,60))
#         cv2.line(img, (center[0], center[1]-radius), (center[0], center[1]-radius-30), stem_color, 5)
#         leaf_color = (0, randint(150,200), 0)
#         cv2.ellipse(img, (center[0]+20, center[1]-radius-20), (30, 15), 45, 0, 360, leaf_color, -1)
#     elif obj_type == 'ball':
#         # Seam lines for tennis ball
#         seam_color = (255, 255, 255)
#         cv2.ellipse(img, center, (radius, radius//10), 0, -90, 90, seam_color, 3)
#         cv2.ellipse(img, center, (radius//10, radius), 90, -90, 90, seam_color, 3)
    
#     # Blur for soft look
#     img = cv2.GaussianBlur(img, (5,5), 0)
    
#     cv2.imwrite(f"{save_folder}/green_{obj_type}_{i:07d}.jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 90])




# pip install torch torchvision torchaudio
# pip install diffusers transformers



# import os
# from diffusers import StableDiffusionPipeline
# import torch

# # Create 'images' folder if it doesn't exist
# if not os.path.exists('images'):
#     os.makedirs('images')

# # Load Stable Diffusion model (ensure you have a CUDA-enabled GPU)
# model = StableDiffusionPipeline.from_pretrained("CompVis/stable-diffusion-v-1-4-original", torch_dtype=torch.float16)
# model.to("cuda")

# # Function to generate and save an image from a prompt
# def generate_image(prompt, idx):
#     # Generate image based on the prompt
#     image = model(prompt).images[0]
    
#     # Save the generated image to the 'images' folder
#     image.save(f"images/green_object_{idx}.png")
#     print(f"Saved image as images/green_object_{idx}.png")

# # List of diverse prompts for generating green objects
# prompts = [
#     "A green apple on a wooden table",
#     "A green pear with water droplets",
#     "A green watermelon slice",
#     "A bunch of green grapes",
#     "A green tree in a lush forest",
#     "A large green cactus in a desert",
#     "A green plant in a modern living room",
#     "A green bamboo forest with sunlight streaming through",
#     "A green fern growing on a rock",
#     "A green frog sitting on a lily pad",
#     "A green chameleon on a tree branch",
#     "A green snake in the jungle",
#     "A green parrot sitting on a branch",
#     "A green turtle swimming in the ocean",
#     "A green sports car on a race track",
#     "A green electric car parked in the city",
#     "A green bicycle on a mountain trail",
#     "A green vintage car on a dusty road",
#     "A green military jeep in the forest",
#     "A green futuristic robot standing in a city",
#     "A green spaceship landing on a new planet",
#     "A green drone flying over a city",
#     "A green AI assistant working on a computer",
#     "A green glass building reflecting the sky",
#     "A futuristic green skyscraper in a city skyline",
#     "A green cottage surrounded by trees",
#     "A green castle on a hill",
#     "A green umbrella in the rain",
#     "A green gift box with a ribbon",
#     "A green bicycle leaning against a tree",
#     "A green hat on a sandy beach",
#     "A green ice cream cone with sprinkles",
# "Any green object"
# ]

# # Generate and save 1000 images using the prompts
# for i in range(1000):
#     prompt = prompts[i % len(prompts)]  # Rotate through prompts
#     generate_image(prompt, i)




# import os
# from diffusers import StableDiffusionPipeline
# import torch

# # ------------------ Important Settings ------------------
# MODEL_ID = "CompVis/stable-diffusion-v1-4"      # Yeh sahi ID hai (diffusers ke liye)
# # Agar better quality chahiye toh try kar sakta hai: "runwayml/stable-diffusion-v1-5"

# # Images folder bana le
# if not os.path.exists('images'):
#     os.makedirs('images')

# print("Loading model... (pehle baar thoda time lagega ~5-15 min)")

# # Model load karo with memory optimizations
# pipe = StableDiffusionPipeline.from_pretrained(
#     MODEL_ID,
#     torch_dtype=torch.float16,          # Half precision → kam VRAM
#     variant="fp16",                     # FP16 weights (tez + kam memory)
#     use_safetensors=True,               # Safe & modern format
# )

# # Yeh sab memory aur speed ke liye bahut zaroori hai!
# pipe.to("cuda")                         # GPU pe bhejo
# pipe.enable_xformers_memory_efficient_attention()   # ★ Speed + memory kam
# pipe.enable_attention_slicing()         # Aur kam VRAM (thoda slow but safe)

# # Optional: agar bahut kam VRAM hai (6GB ya kam) toh yeh bhi add kar sakta hai
# # pipe.enable_sequential_cpu_offload()   # VRAM ko 4-5GB tak le aayega (slow ho jaayega)

# print("Model loaded successfully! Ab generation start karte hain...")

# # Function to generate & save image
# def generate_image(prompt, idx):
#     print(f"Generating {idx+1}/1000 → Prompt: {prompt}")
    
#     # Generate (guidance_scale=7.5 achha balance deta hai)
#     image = pipe(
#         prompt,
#         num_inference_steps=30,         # 30-50 ke beech best (tez + quality)
#         guidance_scale=7.5,
#         negative_prompt="blurry, low quality, deformed, ugly"   # ← better results
#     ).images[0]
    
#     # Save kar do
#     filename = f"images/green_object_{idx:04d}.png"  # 0001, 0002... style
#     image.save(filename)
#     print(f"Saved → {filename}\n")

# # Tera original prompts list (last wala generic bhi rakha)
# prompts = [
#     "A green apple on a wooden table",
#     "A green pear with water droplets",
#     "A green watermelon slice",
#     "A bunch of green grapes",
#     "A green tree in a lush forest",
#     "A large green cactus in a desert",
#     "A green plant in a modern living room",
#     "A green bamboo forest with sunlight streaming through",
#     "A green fern growing on a rock",
#     "A green frog sitting on a lily pad",
#     "A green chameleon on a tree branch",
#     "A green snake in the jungle",
#     "A green parrot sitting on a branch",
#     "A green turtle swimming in the ocean",
#     "A green sports car on a race track",
#     "A green electric car parked in the city",
#     "A green bicycle on a mountain trail",
#     "A green vintage car on a dusty road",
#     "A green military jeep in the forest",
#     "A green futuristic robot standing in a city",
#     "A green spaceship landing on a new planet",
#     "A green drone flying over a city",
#     "A green AI assistant working on a computer",
#     "A green glass building reflecting the sky",
#     "A futuristic green skyscraper in a city skyline",
#     "A green cottage surrounded by trees",
#     "A green castle on a hill",
#     "A green umbrella in the rain",
#     "A green gift box with a ribbon",
#     "A green bicycle leaning against a tree",
#     "A green hat on a sandy beach",
#     "A green ice cream cone with sprinkles",
#     "Any green object, vibrant emerald color, detailed"
# ]

# # 1000 images generate karo (loop prompts pe rotate karega)
# for i in range(1000):
#     prompt = prompts[i % len(prompts)]
#     generate_image(prompt, i)

# print("Done! 1000 images ban gaye 'images' folder mein 🔥")


# import os
# import torch
# from diffusers import StableDiffusionPipeline

# # ------------------ Important Settings ------------------
# MODEL_ID = "CompVis/stable-diffusion-v1-4"

# # Images folder create karo
# if not os.path.exists("images"):
#     os.makedirs("images")

# print("Loading model... (CPU pe first time 10–20 min lag sakta hai ⏳)")

# # ================= LOAD MODEL (CPU SAFE) =================
# pipe = StableDiffusionPipeline.from_pretrained(
#     MODEL_ID,
#     torch_dtype=torch.float32,     # CPU ke liye safest
#     safety_checker=None,          # thoda fast load ke liye
#     use_safetensors=True
# )

# # CPU pe run karo
# pipe = pipe.to("cpu")

# # Memory optimization (CPU friendly)
# pipe.enable_attention_slicing()

# print("✅ Model loaded successfully! Ab image generation start hoga...\n")

# # ================= IMAGE GENERATOR FUNCTION =================
# def generate_image(prompt, idx):
#     try:
#         print(f"🖼️ Generating {idx+1} → {prompt}")

#         result = pipe(
#             prompt=prompt,
#             num_inference_steps=20,        # CPU ke liye optimized
#             guidance_scale=7.0,
#             negative_prompt="blurry, low quality, deformed, ugly"
#         )

#         image = result.images[0]

#         filename = f"images/green_object_{idx:04d}.png"
#         image.save(filename)

#         print(f"✅ Saved → {filename}\n")

#     except Exception as e:
#         print("❌ Image generation failed:", e)


# # ================= PROMPTS =================
# prompts = [
#     "A green apple on a wooden table",
#     "A green pear with water droplets",
#     "A green watermelon slice",
#     "A bunch of green grapes",
#     "A green tree in a lush forest",
#     "A green cactus in a desert",
#     "A green plant in a modern living room",
#     "A green bamboo forest with sunlight",
#     "A green frog sitting on a lily pad",
#     "A green parrot on a branch",
#     "A green sports car on a race track",
#     "A futuristic green robot in a city",
#     "A green glass skyscraper reflecting the sky",
#     "A green gift box with ribbon",
#     "Any green object, vibrant emerald color, ultra detailed"
# ]

# # ⚠️ CPU slow hota hai — pehle testing ke liye kam images banao
# TOTAL_IMAGES = 3        # pehle sirf 3 test karo

# for i in range(TOTAL_IMAGES):
#     prompt = prompts[i % len(prompts)]
#     generate_image(prompt, i)

# print("🎉 Done! Images 'images' folder me save ho chuki hain.")



import os
import torch
from diffusers import StableDiffusionPipeline

MODEL_ID = "CompVis/stable-diffusion-v1-4"

if not os.path.exists("images"):
    os.makedirs("images")

print("Loading model...")

pipe = StableDiffusionPipeline.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.float32,
    safety_checker=None
)

pipe.to("cpu")

# Extreme speed optimizations
pipe.enable_attention_slicing()
pipe.enable_vae_slicing()
pipe.enable_vae_tiling()

torch.set_num_threads(8)   # apne CPU cores ke hisab se set karo

print("✅ Model loaded!\n")

def generate_image(prompt, idx):
    print(f"⚡ Generating {idx+1}")

    image = pipe(
        prompt=prompt,
        num_inference_steps=10,   # 🔥 bahut kam steps
        guidance_scale=5.5,
    ).images[0]

    filename = f"images/img_{idx:03d}.png"
    image.save(filename)
    print(f"✅ Saved → {filename}\n")

prompts = [
    "A green apple on a wooden table",
    "A green car in city",
    "A green forest with sunlight"
]

TOTAL_IMAGES = 3

for i in range(TOTAL_IMAGES):
    generate_image(prompts[i % len(prompts)], i)

print("Done!")