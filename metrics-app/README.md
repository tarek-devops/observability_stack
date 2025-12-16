## Run Metrics Application

```bash
cd metrics-app
pip install -r requirements.txt

# Test directly
python simple-metrics-sender.py

# Build Windows .exe
pip install pyinstaller
# Add pyinstaller to the PATH
$env:Path += ";C:\Users\tderi\AppData\Roaming\Python\Python313\Scripts"

# Build .exe file from python script
pyinstaller --onefile --name metrics-sender simple-metrics-sender.py
# Output: dist/metrics-sender.exe

./metrics-sender.exe  # Windows
```