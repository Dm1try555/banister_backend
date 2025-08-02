# Changelog - Banister Backend

## [2025-01-31] - Major Updates

### 🔧 **API Improvements**

#### **Profile Management**
- ✅ **Role Change Protection**: Added security restriction preventing role changes via PUT/PATCH profile endpoints
- ✅ **Enhanced Validation**: Improved validation for PUT and PATCH methods on `/auth/profile/` endpoint
- ✅ **Profile Photo Integration**: Fixed `profile_photo_url` display in profile responses

#### **Profile Photo System**
- ✅ **Unified Endpoint**: Consolidated `upload` and `quick-change` into single universal endpoint
- ✅ **Automatic Cleanup**: Automatically deletes old photos when uploading new ones
- ✅ **Enhanced Error Handling**: Better error messages and validation
- ✅ **Swagger Integration**: Fixed file upload interface in Swagger UI

#### **Authentication & Security**
- ✅ **Token Management**: Added `/clear-token/` endpoint for Swagger UI token clearing
- ✅ **Logout Enhancement**: Improved logout with instructions for token clearing
- ✅ **Role-Based Validation**: Enhanced profile photo requirements for providers and management

### 🗂️ **File Storage & MinIO**

#### **Unified Photo Upload**
- **Endpoint**: `POST /api/v1/files/profile-photo/upload/`
- **Features**:
  - Universal upload/change functionality
  - Automatic old file deletion
  - Image processing and validation
  - MinIO storage integration
  - Public URL generation

#### **Database Models**
- **User Model**: Enhanced with `get_profile_photo_url()` and `has_required_profile_photo()` methods
- **ProfilePhoto Model**: Improved relationship with FileStorage
- **FileStorage Model**: Added `file_url` property for presigned URLs

### 🔄 **Code Refactoring**

#### **Serializers**
- ✅ **Circular Dependency Fix**: Created `SimpleUserSerializer` to break import cycles
- ✅ **Provider Profile**: Fixed `provider_profile` serialization in `ProviderUserSerializer`
- ✅ **Profile Photo URL**: Corrected URL generation in serializers

#### **Views**
- ✅ **ProfileView**: Added role change protection and improved validation
- ✅ **FileStorage Views**: Enhanced with proper parser classes and error handling
- ✅ **Swagger Documentation**: Fixed file upload configuration

#### **Models**
- ✅ **User Model**: Improved profile photo URL retrieval using Django ORM
- ✅ **FileStorage Model**: Enhanced URL generation for MinIO integration

### 📚 **Documentation Updates**

#### **AUTHENTICATION_API.md**
- ✅ Added profile photo management section
- ✅ Documented role change restrictions
- ✅ Added new error types and responses
- ✅ Updated security considerations
- ✅ Added token management endpoints

#### **MINIO_IMPLEMENTATION.md**
- ✅ Updated API endpoints to reflect unified structure
- ✅ Enhanced response examples
- ✅ Added new features and security measures
- ✅ Updated usage examples

### 🚀 **New Features**

#### **Profile Photo Management**
```bash
# Universal upload/change endpoint
POST /api/v1/files/profile-photo/upload/
Content-Type: multipart/form-data
Authorization: Bearer <token>

# File upload in Swagger UI
# - Choose File button now available
# - Proper multipart/form-data handling
# - Automatic file validation
```

#### **Security Enhancements**
```bash
# Role change protection
PUT/PATCH /api/v1/auth/profile/
# Returns error if role field is included

# Token management
GET /api/v1/auth/clear-token/
# Provides JavaScript to clear Swagger UI token
```

### 🐛 **Bug Fixes**

#### **Profile Photo Issues**
- ✅ Fixed `profile_photo_url` being `null` in GET profile responses
- ✅ Resolved circular dependency in serializers
- ✅ Fixed duplicate key constraint errors
- ✅ Corrected URL generation for MinIO files

#### **Swagger UI Issues**
- ✅ Fixed "Choose File" button missing
- ✅ Resolved `SwaggerGenerationError` for file uploads
- ✅ Added proper parser classes for multipart data
- ✅ Enhanced documentation for file upload endpoints

#### **Authentication Issues**
- ✅ Added custom JWT token error handling
- ✅ Improved error messages for invalid/expired tokens
- ✅ Better error responses for authentication failures

### 📦 **Dependencies**
- ✅ Added `Pillow==11.0.0` for image processing
- ✅ Enhanced MinIO integration
- ✅ Improved error handling middleware

### 🔒 **Security Improvements**
- ✅ Role change prevention via profile endpoints
- ✅ Enhanced file validation and processing
- ✅ Improved token management
- ✅ Better error handling and logging
- ✅ Custom JWT token error handling

---

## **Migration Notes**

### **For Developers**
1. **API Changes**: 
   - Removed `/quick-change/` endpoint
   - Unified photo upload under `/upload/`
   - Added role change protection

2. **Database**: 
   - No migrations required
   - Existing data remains compatible

3. **Frontend Integration**:
   - Update photo upload endpoints
   - Handle new error responses
   - Implement token clearing functionality

### **For Users**
- ✅ **Simplified Photo Upload**: Single endpoint for all photo operations
- ✅ **Better Error Messages**: Clear feedback for validation issues
- ✅ **Enhanced Security**: Protected against unauthorized role changes
- ✅ **Improved UX**: Better Swagger UI integration

---

## **Testing Checklist**

### **Profile Management**
- [ ] PUT/PATCH profile with role field (should fail)
- [ ] Profile photo upload via Swagger UI
- [ ] Profile photo replacement
- [ ] GET profile with photo URL display

### **Authentication**
- [ ] Login with different roles
- [ ] Token refresh
- [ ] Logout and token clearing
- [ ] Clear token endpoint

### **File Upload**
- [ ] Valid image formats (JPG, PNG, GIF)
- [ ] File size validation (max 5MB)
- [ ] Invalid file rejection
- [ ] Old file cleanup on replacement

### **Error Handling**
- [ ] Role change attempts
- [ ] Invalid file uploads
- [ ] Missing required photos
- [ ] Network errors
- [ ] Invalid token errors
- [ ] Expired token errors
- [ ] Missing token errors

---

**Status**: ✅ **Production Ready**
**Version**: 2.0.0
**Date**: 2025-01-31 