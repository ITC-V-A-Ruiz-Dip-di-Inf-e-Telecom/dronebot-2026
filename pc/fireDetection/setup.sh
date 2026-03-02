#!/bin/bash

# This script sets up PyTorch with CUDA support for GPU acceleration

set -e

echo "Fire Detection Setup"
echo ""

echo "📦 Installing pixi dependencies..."
pixi install

echo ""
echo "🔧 Setting up PyTorch with CUDA support..."
echo ""

echo "Removing CPU-only PyTorch..."
pixi run pip uninstall torch torchvision -y

echo ""
echo "Installing PyTorch with CUDA 12.1..."
pixi run pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

echo ""
echo "Installing missing dependencies..."
pixi run pip install ultralytics-thop

echo ""
echo "✅ Setup Complete!"
echo ""
