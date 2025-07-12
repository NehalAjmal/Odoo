# ReWear - Community Clothing Exchange

A full-stack web application promoting sustainable fashion through clothing swaps.

## 🌱 About ReWear

ReWear is a community-driven platform where users can exchange clothes, earn points, and contribute to sustainable fashion. Users can upload items, send swap requests, redeem clothes with points, and track their environmental impact through our gamification system.

## 🚀 Tech Stack

- **Frontend**: React.js with Tailwind CSS
- **Backend**: Django with REST Framework
- **Database**: MySQL
- **Authentication**: Django Auth (JWT)
- **Image Storage**: Cloudinary
- **Hosting**: 
  - Frontend: Vercel/Netlify
  - Backend: Render/Railway

## 🎨 Design System

Our color palette represents sustainability, freshness, trust, and bold actions:

- **Primary**: #FF1F35 (Primary actions, buttons, icons)
- **Brand Dark**: #438973 (Header/nav background, tags)
- **Brand Accent**: #2DC8BB (Secondary buttons, hover, progress)
- **Background**: #F0FFFO (Body background, card backgrounds)
- **Text Dark**: #0B090B (Primary text, footer, headings)

## 📁 Project Structure

```
rewear/
├── client/          # React frontend
│   ├── components/
│   ├── pages/
│   ├── services/
│   ├── assets/
│   └── tailwind.config.js
├── server/          # Django backend
│   ├── users/
│   ├── items/
│   ├── swaps/
│   ├── points/
│   ├── admin/
│   └── settings.py
└── README.md
```

## 🔧 Setup Instructions

### Backend Setup
1. Navigate to the `server` directory
2. Create virtual environment: `python -m venv venv`
3. Activate virtual environment: `source venv/bin/activate` (macOS/Linux)
4. Install dependencies: `pip install -r requirements.txt`
5. Set up MySQL database
6. Run migrations: `python manage.py migrate`
7. Create superuser: `python manage.py createsuperuser`
8. Start server: `python manage.py runserver`

### Frontend Setup
1. Navigate to the `client` directory
2. Install dependencies: `npm install`
3. Start development server: `npm start`

## ✨ Features

### User Features
- Register/Login with email and password
- Upload items with photos, descriptions, and details
- Send and receive swap requests
- Point-based redemption system
- Track swap status and history
- View public profile galleries
- Join Mystery Swap Box events

### Admin Features
- Approve or reject item listings
- Content moderation
- Analytics dashboard
- Badge and green score management

### Gamification
- **Green Score**: Calculated based on items listed, swaps completed, and environmental impact
- **Badges**: Achievement system for user engagement
- **Mystery Swap Box**: AI-powered matching system

## 🌍 Environmental Impact

ReWear promotes sustainability by:
- Extending clothing lifecycles
- Reducing textile waste
- Encouraging circular fashion
- Tracking environmental savings

## 📱 Mobile-First Design

The platform is optimized for mobile devices with responsive design principles, ensuring a seamless experience across all screen sizes.

## 🤝 Contributing

We welcome contributions! Please read our contributing guidelines and submit pull requests for any improvements.

## 📄 License

This project is licensed under the MIT License.