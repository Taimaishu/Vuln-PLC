#!/bin/bash
echo "Fixing Docker ContainerConfig error..."
echo ""
echo "Step 1: Stopping all containers..."
sudo docker-compose down 2>/dev/null || true

echo ""
echo "Step 2: Removing old containers..."
sudo docker-compose rm -f 2>/dev/null || true

echo ""
echo "Step 3: Pruning volumes..."
sudo docker volume prune -f

echo ""
echo "Step 4: Starting fresh..."
sudo docker-compose up -d

echo ""
echo "Step 5: Waiting for services to initialize..."
sleep 10

echo ""
echo "Step 6: Checking status..."
sudo docker-compose ps

echo ""
echo "Done! Containers should be running now."
