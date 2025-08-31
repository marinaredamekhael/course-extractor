# Deployment Guide for Course Extractor

This guide will help you deploy your Flask Course Extractor app to GitHub and make it publicly accessible.

## Option 1: Deploy to Heroku (Recommended for Public Access)

### Prerequisites
- GitHub account
- Heroku account (free tier available)
- Git installed on your computer

### Step 1: Prepare Your Repository

1. **Initialize Git Repository** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **Create GitHub Repository**:
   - Go to [GitHub](https://github.com)
   - Click "New repository"
   - Name it `course-extractor`
   - Make it public
   - Don't initialize with README (we already have one)
   - Click "Create repository"

3. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/course-extractor.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy to Heroku

1. **Install Heroku CLI**:
   - Download from [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
   - Or use: `npm install -g heroku`

2. **Login to Heroku**:
   ```bash
   heroku login
   ```

3. **Create Heroku App**:
   ```bash
   heroku create your-course-extractor-app
   ```

4. **Deploy**:
   ```bash
   git push heroku main
   ```

5. **Open Your App**:
   ```bash
   heroku open
   ```

Your app will be available at: `https://your-course-extractor-app.herokuapp.com`

## Option 2: Deploy to Railway (Alternative)

1. **Go to [Railway](https://railway.app)**
2. **Connect your GitHub account**
3. **Select your repository**
4. **Deploy automatically**

## Option 3: Deploy to Render (Alternative)

1. **Go to [Render](https://render.com)**
2. **Connect your GitHub account**
3. **Create a new Web Service**
4. **Select your repository**
5. **Configure build settings**

## Environment Variables (if needed)

If you need to set environment variables:

```bash
# For Heroku
heroku config:set VARIABLE_NAME=value

# For Railway/Render, use their web interface
```

## Troubleshooting

### Common Issues:

1. **Build Failures**:
   - Check that all dependencies are in `requirements.txt`
   - Ensure `Procfile` is correct
   - Verify Python version in `runtime.txt`

2. **App Crashes**:
   - Check logs: `heroku logs --tail`
   - Ensure all imports are working
   - Verify environment variables

3. **Static Files Not Loading**:
   - Check that static files are in the correct directory
   - Verify Flask static folder configuration

## Making Your App Public

Once deployed, your app will have a public URL that anyone can access. Share this URL with others to use your Course Extractor!

## Updating Your App

To update your deployed app:

```bash
git add .
git commit -m "Update description"
git push origin main
git push heroku main  # or your deployment platform
```

## Support

If you encounter issues:
1. Check the platform's documentation
2. Review error logs
3. Ensure all files are properly committed to Git
