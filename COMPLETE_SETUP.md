# 🌾 FARMER ASSISTANT - COMPLETE SETUP SUMMARY

## ✅ SYSTEM STATUS

All services have been configured and are ready to use!

### Running Services:

- ✅ **Image Classifier API** - Port 8000
- ✅ **Reasoning Layer API** - Port 8002
- ✅ **Expo Development Server** - Port 8081

---

## 🚀 QUICK START - ONE COMMAND

### Start Everything:

```powershell
.\start_all.ps1
```

This single command will:

1. Kill any existing processes on ports 8000, 8002, 8081
2. Start Image Classifier API in a new window
3. Start Reasoning Layer API in a new window
4. Start Expo Dev Server in a new window
5. Verify all services are running
6. Display access URLs and QR code

### Stop Everything:

```powershell
.\stop_all.ps1
```

### Test Everything:

```powershell
.\test_all.ps1
```

---

## 📱 MOBILE APP USAGE

### Option 1: Physical Device (Recommended)

1. Install **Expo Go** app from Play Store/App Store
2. Make sure phone and PC are on **same WiFi**
3. Run `.\start_all.ps1`
4. **Scan QR code** from Expo window with Expo Go app
5. App will load automatically

**Important:** Update your IP address in `atharva_UI\services\api.ts`:

```typescript
const BACKEND_HOST = "YOUR_IP_HERE"; // Find with: ipconfig
```

### Option 2: Emulator

1. Start Android Studio emulator or Xcode simulator
2. Run `.\start_all.ps1`
3. In Expo window, press:
   - `a` for Android
   - `i` for iOS
   - `w` for web browser

---

## 🎓 MODEL TRAINING

### Quick Test (30-60 minutes, 10 epochs):

```powershell
cd image_classifier
..\.venv\Scripts\python.exe train.py --dataset "C:\Users\advdi\.cache\kagglehub\datasets\emmarex\plantdisease\versions\1\PlantVillage\PlantVillage" --epochs 10 --batch-size 32 --lr 0.001 --output output
```

### Full Training (6-10 hours, 100 epochs):

```powershell
.\train_model.ps1
```

**Note:** The app works even without a trained model (it will return mock responses for testing)

---

## 📋 ALL AVAILABLE SCRIPTS

| Script            | Purpose                     | Duration   |
| ----------------- | --------------------------- | ---------- |
| `start_all.ps1`   | Start all 3 services        | 15 seconds |
| `stop_all.ps1`    | Stop all services           | 5 seconds  |
| `test_all.ps1`    | Run automated tests         | 30 seconds |
| `train_model.ps1` | Train ML model (100 epochs) | 6-10 hours |

---

## 🔧 MANUAL CONTROLS

### Backend Services

#### Image Classifier (Port 8000):

```powershell
cd D:\HACATHONS\ATHARVA
.venv\Scripts\python.exe image_classifier\api.py
```

#### Reasoning Layer (Port 8002):

```powershell
cd D:\HACATHONS\ATHARVA
.venv\Scripts\uvicorn.exe reasoning_layer.main:app --host 0.0.0.0 --port 8002
```

### Frontend

#### Expo Server (Port 8081):

```powershell
cd D:\HACATHONS\ATHARVA\atharva_UI
npx expo start
```

---

## 🌐 API ENDPOINTS

### Image Classifier API (http://localhost:8000)

- `GET /health` - Check if service is running and model status
- `POST /classify` - Upload image for disease classification
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /` - Root endpoint with welcome message

### Reasoning Layer API (http://localhost:8002)

- `POST /reason` - Get agricultural advice based on classification
- `GET /docs` - Interactive API documentation (Swagger UI)

### Expo Dev Server (http://localhost:8081)

- Main development server for React Native app
- Provides QR code for mobile testing
- Hot reload functionality

---

## 🧪 TESTING WORKFLOW

### Automated Testing:

```powershell
.\test_all.ps1
```

This checks:

- ✅ All ports are listening (8000, 8002, 8081)
- ✅ HTTP endpoints responding
- ✅ Model loaded status
- ✅ Critical files exist
- ✅ Python packages installed
- ✅ Node.js dependencies installed

### Manual Testing:

#### Test Image Classifier:

```powershell
# Check health
curl http://localhost:8000/health

# View API docs
start http://localhost:8000/docs
```

#### Test Reasoning Layer:

```powershell
# View API docs
start http://localhost:8002/docs
```

#### Test Expo App:

1. Start services: `.\start_all.ps1`
2. Scan QR code with Expo Go
3. Test camera functionality
4. Test chat functionality
5. Test image classification workflow

---

## 📁 PROJECT STRUCTURE

```
D:\HACATHONS\ATHARVA\
│
├── 📄 start_all.ps1              # ⭐ START EVERYTHING
├── 📄 stop_all.ps1               # Stop all services
├── 📄 test_all.ps1               # Test all services
├── 📄 train_model.ps1            # Train ML model
├── 📄 QUICKSTART_GUIDE.md        # Detailed guide
│
├── 📦 image_classifier/          # Backend: Image Classification
│   ├── api.py                   # FastAPI server
│   ├── train.py                 # Training script
│   ├── model.py                 # MobileNetV3 model
│   ├── dataset.py               # Dataset handling
│   ├── infer.py                 # Inference logic
│   ├── requirements.txt         # Python dependencies
│   └── output/                  # Trained model files
│       ├── best_model.pth       # Model weights
│       ├── class_map.json       # Class mappings
│       └── training_history.json
│
├── 📦 reasoning_layer/           # Backend: AI Reasoning
│   ├── main.py                  # FastAPI server
│   ├── requirements.txt         # Python dependencies
│   └── models/                  # LLM models (optional)
│
├── 📱 atharva_UI/                # Frontend: React Native App
│   ├── App.tsx                  # Main app entry
│   ├── package.json             # Node dependencies
│   ├── screens/                 # App screens
│   │   ├── HomeScreen.tsx
│   │   ├── CameraScreen.tsx
│   │   ├── ChatScreen.tsx
│   │   ├── ProfileScreen.tsx
│   │   ├── NewsScreen.tsx
│   │   └── LoginScreen.tsx
│   ├── services/                # API integration
│   │   ├── api.ts              # ⚠️ Update IP here
│   │   ├── imageService.ts
│   │   └── reasoningService.ts
│   ├── components/              # Reusable components
│   └── navigation/              # Navigation setup
│
└── 📦 .venv/                     # Python virtual environment
```

---

## ⚙️ CONFIGURATION

### Update Backend IP for Mobile Testing

**File:** `atharva_UI\services\api.ts`

**Find your IP:**

```powershell
ipconfig
# Look for "IPv4 Address" under your WiFi/Ethernet adapter
```

**Update the code:**

```typescript
// Line ~13 in api.ts
const BACKEND_HOST = "192.168.YOUR.IP"; // Replace with your actual IP
```

**Example:**

```typescript
const BACKEND_HOST = "192.168.1.100"; // Your computer's IP
```

---

## 🚨 TROUBLESHOOTING

### Problem: Port Already in Use

```powershell
# Option 1: Use stop script
.\stop_all.ps1

# Option 2: Manual kill
netstat -ano | findstr ":8000"
taskkill /F /PID <PID_NUMBER>
```

### Problem: Services Won't Start

```powershell
# Check virtual environment
ls .venv\Scripts\python.exe

# Reinstall Python dependencies
.venv\Scripts\pip install -r requirements.txt

# Check Node.js
node --version

# Reinstall Node dependencies
cd atharva_UI
npm install
```

### Problem: Model Not Loaded

The app works without a trained model (uses fallback responses). To train:

```powershell
.\train_model.ps1
```

### Problem: Can't Connect from Phone

1. Check both devices on same WiFi
2. Update IP in `atharva_UI\services\api.ts`
3. Restart services: `.\stop_all.ps1` then `.\start_all.ps1`
4. Check Windows Firewall (allow Python and Node through firewall)

### Problem: Expo QR Code Not Loading

```powershell
# Clear Expo cache
cd atharva_UI
npx expo start --clear
```

---

## 📊 SYSTEM REQUIREMENTS

- **OS:** Windows 10/11
- **Python:** 3.8+ (with `.venv` virtual environment)
- **Node.js:** 16+
- **RAM:** 8GB minimum, 16GB recommended for training
- **Storage:** 5GB+ free space
- **Network:** Same WiFi for mobile testing

---

## 🎯 TYPICAL WORKFLOW

### Day 1: Initial Setup

```powershell
# 1. Install dependencies (if not done)
.venv\Scripts\pip install -r requirements.txt
cd atharva_UI
npm install
cd ..

# 2. (Optional) Train model overnight
.\train_model.ps1

# 3. Start services
.\start_all.ps1

# 4. Test
.\test_all.ps1
```

### Daily Development:

```powershell
# Start
.\start_all.ps1

# ... develop and test ...

# Stop
.\stop_all.ps1
```

### Before Demo:

```powershell
# 1. Test everything
.\test_all.ps1

# 2. Start services
.\start_all.ps1

# 3. Update IP if on new network
# Edit: atharva_UI\services\api.ts

# 4. Restart Expo (press 'r' in Expo window)
```

---

## 📞 QUICK REFERENCE

### Service URLs:

- Image Classifier: http://localhost:8000/docs
- Reasoning Layer: http://localhost:8002/docs
- Expo Dev: http://localhost:8081

### Key Files to Edit:

- Backend IP: `atharva_UI\services\api.ts`
- Training config: `image_classifier\train.py`
- API logic: `image_classifier\api.py`, `reasoning_layer\main.py`

### Common Commands:

```powershell
# Start everything
.\start_all.ps1

# Stop everything
.\stop_all.ps1

# Test everything
.\test_all.ps1

# Train model
.\train_model.ps1

# Find your IP
ipconfig

# Check ports
netstat -ano | findstr ":8000 :8002 :8081"
```

---

## ✨ WHAT'S WORKING NOW

✅ **Backend Services:**

- Image Classifier API running on port 8000
- Reasoning Layer API running on port 8002
- Both accessible via HTTP
- API documentation available at `/docs`

✅ **Frontend:**

- Expo development server running
- QR code generated for mobile testing
- Hot reload enabled

✅ **Scripts:**

- One-command startup (`start_all.ps1`)
- One-command shutdown (`stop_all.ps1`)
- Automated testing (`test_all.ps1`)
- Model training script (`train_model.ps1`)

✅ **Configuration:**

- Backend IP updated to use port 8002
- API endpoints configured
- Services auto-start in separate windows

---

## 🎉 YOU'RE ALL SET!

To start using the app right now:

1. Run: `.\start_all.ps1`
2. Wait for 3 PowerShell windows to open
3. Look for QR code in "Expo Development Server" window
4. Open Expo Go on your phone
5. Scan the QR code
6. Start testing!

**Happy Farming! 🌾**
