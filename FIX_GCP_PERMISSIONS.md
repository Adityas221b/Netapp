# 🔧 Fix GCP Write Permissions

## Current Issue
- Service Account: `cloudflux-app@robotic-jet-477613-e9.iam.gserviceaccount.com`
- Project: `robotic-jet-477613-e9`
- Bucket: `cloudflux-gcp-bucket-477613`
- Error: `403 Forbidden` when uploading files

## ✅ Solution: Grant Storage Admin Permissions

### Option 1: Using Google Cloud Console (Recommended - 2 minutes)

1. **Go to GCP Console**
   - Visit: https://console.cloud.google.com/
   - Login with your Google account
   - Select project: `robotic-jet-477613-e9`

2. **Navigate to IAM & Admin**
   - Click hamburger menu (☰) → IAM & Admin → IAM
   - Or go directly: https://console.cloud.google.com/iam-admin/iam

3. **Find Your Service Account**
   - Look for: `cloudflux-app@robotic-jet-477613-e9.iam.gserviceaccount.com`
   - Click the pencil icon (✏️) to edit permissions

4. **Add Storage Admin Role**
   - Click "+ ADD ANOTHER ROLE"
   - Search for: "Storage Object Admin"
   - Select: **Storage Object Admin** (roles/storage.objectAdmin)
   - Click "SAVE"

5. **Alternative: Use Storage Admin for Full Access**
   - Role: **Storage Admin** (roles/storage.admin)
   - This gives full control over buckets and objects

---

### Option 2: Using gcloud CLI (1 minute)

```bash
# Set your project
gcloud config set project robotic-jet-477613-e9

# Grant Storage Object Admin role to service account
gcloud projects add-iam-policy-binding robotic-jet-477613-e9 \
  --member="serviceAccount:cloudflux-app@robotic-jet-477613-e9.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

# Alternative: Grant Storage Admin for full access
gcloud projects add-iam-policy-binding robotic-jet-477613-e9 \
  --member="serviceAccount:cloudflux-app@robotic-jet-477613-e9.iam.gserviceaccount.com" \
  --role="roles/storage.admin"
```

---

### Option 3: Bucket-Level Permissions (Most Secure)

If you want to grant permissions only to specific bucket:

```bash
# Grant write access to specific bucket only
gsutil iam ch serviceAccount:cloudflux-app@robotic-jet-477613-e9.iam.gserviceaccount.com:roles/storage.objectAdmin \
  gs://cloudflux-gcp-bucket-477613
```

---

## 🔍 Verify Permissions

After granting permissions, test with this command:

```bash
cd /home/bitreaper/Desktop/Netapp/cloudflux-ai/backend && python3 << 'TEST_GCP'
import os
from google.cloud import storage

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './gcp-credentials.json'
client = storage.Client(project='robotic-jet-477613-e9')
bucket = client.bucket('cloudflux-gcp-bucket-477613')

# Test write permission
test_blob = bucket.blob('test-write-permission.txt')
try:
    test_blob.upload_from_string('Testing write permissions!')
    print("✅ SUCCESS! Write permissions working!")
    print(f"   File uploaded: test-write-permission.txt")
    
    # Cleanup
    test_blob.delete()
    print("✅ Cleanup successful")
except Exception as e:
    print(f"❌ FAILED: {e}")
TEST_GCP
```

---

## 📋 Required IAM Roles

Choose ONE of these roles:

| Role | Permission | Best For |
|------|-----------|----------|
| **Storage Object Admin** | Read/Write objects | ✅ Recommended - Our use case |
| **Storage Admin** | Full bucket control | If you need to create/delete buckets |
| **Storage Object Creator** | Write only | If you only need uploads |
| **Storage Object Viewer** | Read only | Current limited access ❌ |

---

## 🎯 What We Need

For CloudFlux AI migration to work, we need:
- ✅ Read objects from bucket (currently working)
- ❌ Write objects to bucket (currently blocked - 403)
- ❌ Delete objects (optional, for cleanup)

**Solution: Grant "Storage Object Admin" role**

---

## 🚀 After Fixing Permissions

Test the migration again:

```bash
# Run the full GCP migration test
bash /tmp/test_gcp_migrations.sh
```

You should see:
- ✅ AWS → GCP migrations working
- ✅ Azure → GCP migrations working
- ✅ GCP → AWS migrations working
- ✅ GCP → Azure migrations working

---

## 🔐 Security Best Practice

For production:
1. Use **bucket-level permissions** (most secure)
2. Create separate service accounts per environment
3. Use Workload Identity Federation instead of service account keys
4. Rotate service account keys regularly
5. Enable Cloud Audit Logs for tracking

---

## ⚠️ Troubleshooting

If permissions don't work immediately:
1. Wait 60 seconds for IAM propagation
2. Restart your backend server
3. Check IAM policy with: `gcloud projects get-iam-policy robotic-jet-477613-e9`
4. Verify bucket exists: `gsutil ls gs://cloudflux-gcp-bucket-477613`

---

## 📞 Need Help?

If you encounter issues:
1. Check current permissions:
   ```bash
   gcloud projects get-iam-policy robotic-jet-477613-e9 \
     --flatten="bindings[].members" \
     --filter="bindings.members:cloudflux-app@robotic-jet-477613-e9.iam.gserviceaccount.com"
   ```

2. Verify service account is enabled:
   ```bash
   gcloud iam service-accounts describe cloudflux-app@robotic-jet-477613-e9.iam.gserviceaccount.com
   ```

3. Check bucket permissions:
   ```bash
   gsutil iam get gs://cloudflux-gcp-bucket-477613
   ```

---

**Estimated Time: 2-5 minutes**

Once fixed, all 6 migration routes will work! 🎉
