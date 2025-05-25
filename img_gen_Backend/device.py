import torch

# Check if CUDA is available
if torch.cuda.is_available():
    print("CUDA is available. Using GPU.")
    device = torch.device("cuda")  # Use GPU
else:
    print("CUDA is not available. Using CPU.")
    device = torch.device("cpu")  # Use CPU

# Print the device that the model is using
print(f"Device used: {device}")
