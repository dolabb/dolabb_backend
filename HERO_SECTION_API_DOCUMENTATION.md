# Hero Section API Documentation

## API Endpoints

### 1. Public Endpoint - Get Hero Section

**GET** `/api/products/hero-section/`

No authentication required. Returns the active hero section for the homepage.

### 2. Admin Endpoint - Get Hero Section

**GET** `/api/admin/hero-section/`

Requires admin authentication. Returns hero section data (including inactive).

### 3. Admin Endpoint - Update Hero Section

**PUT** `/api/admin/hero-section/update/`

Requires admin authentication. Updates the hero section with new content.

---

## Response Structure

### Success Response

```json
{
  "success": true,
  "heroSection": {
    "id": "507f1f77bcf86cd799439011",
    "backgroundType": "gradient",
    "imageUrl": "https://example.com/uploads/hero/hero_abc123.jpg",
    "singleColor": "#4F46E5",
    "gradientColors": ["#667eea", "#764ba2"],
    "gradientDirection": "to right",
    "title": "Welcome to Dolabb",
    "subtitle": "Your marketplace for amazing products",
    "buttonText": "Get Started",
    "buttonLink": "/products",
    "textColor": "#FFFFFF",
    "isActive": true,
    "createdAt": "2024-01-15T10:30:00.000Z",
    "updatedAt": "2024-01-20T14:45:00.000Z"
  }
}
```

### Error Response

```json
{
  "success": false,
  "error": "Error message here"
}
```

---

## Frontend Implementation

### TypeScript Interface

```typescript
interface HeroSection {
  id: string | null;
  backgroundType: 'image' | 'single_color' | 'gradient';
  imageUrl: string;
  singleColor: string;
  gradientColors: string[];
  gradientDirection: string;
  title: string;
  subtitle: string;
  buttonText: string;
  buttonLink: string;
  textColor: string;
  isActive: boolean;
  createdAt: string | null;
  updatedAt: string | null;
}

interface HeroSectionResponse {
  success: boolean;
  heroSection: HeroSection;
  error?: string;
}
```

### React Component Example

```tsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const HeroSection: React.FC = () => {
  const [heroData, setHeroData] = useState<HeroSection | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchHeroSection();
  }, []);

  const fetchHeroSection = async () => {
    try {
      setLoading(true);
      const response = await axios.get<HeroSectionResponse>(
        'https://your-api-domain.com/api/products/hero-section/'
      );

      if (response.data.success) {
        setHeroData(response.data.heroSection);
      } else {
        setError(response.data.error || 'Failed to load hero section');
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Network error');
    } finally {
      setLoading(false);
    }
  };

  const getBackgroundStyle = (): React.CSSProperties => {
    if (!heroData) return {};

    switch (heroData.backgroundType) {
      case 'image':
        return {
          backgroundImage: `url(${heroData.imageUrl})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
        };

      case 'single_color':
        return {
          backgroundColor: heroData.singleColor,
        };

      case 'gradient':
        const gradientString = `linear-gradient(${
          heroData.gradientDirection
        }, ${heroData.gradientColors.join(', ')})`;
        return {
          background: gradientString,
        };

      default:
        return {};
    }
  };

  if (loading) {
    return <div className='hero-loading'>Loading...</div>;
  }

  if (error || !heroData || !heroData.isActive) {
    return null; // Don't show hero if inactive or error
  }

  return (
    <section
      className='hero-section'
      style={{
        ...getBackgroundStyle(),
        color: heroData.textColor,
        minHeight: '500px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        textAlign: 'center',
        padding: '2rem',
        position: 'relative',
      }}
    >
      {/* Overlay for better text readability on images */}
      {heroData.backgroundType === 'image' && (
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.4)',
            zIndex: 1,
          }}
        />
      )}

      <div style={{ position: 'relative', zIndex: 2, maxWidth: '800px' }}>
        <h1
          style={{
            fontSize: '3rem',
            fontWeight: 'bold',
            marginBottom: '1rem',
            color: heroData.textColor,
          }}
        >
          {heroData.title}
        </h1>

        {heroData.subtitle && (
          <p
            style={{
              fontSize: '1.5rem',
              marginBottom: '2rem',
              color: heroData.textColor,
            }}
          >
            {heroData.subtitle}
          </p>
        )}

        {heroData.buttonText && heroData.buttonLink && (
          <a
            href={heroData.buttonLink}
            style={{
              display: 'inline-block',
              padding: '1rem 2rem',
              backgroundColor: heroData.textColor,
              color:
                heroData.backgroundType === 'image'
                  ? '#000'
                  : heroData.backgroundType === 'single_color'
                  ? heroData.singleColor
                  : heroData.gradientColors[0],
              textDecoration: 'none',
              borderRadius: '8px',
              fontWeight: 'bold',
              transition: 'transform 0.2s',
              cursor: 'pointer',
            }}
            onMouseEnter={e => {
              e.currentTarget.style.transform = 'scale(1.05)';
            }}
            onMouseLeave={e => {
              e.currentTarget.style.transform = 'scale(1)';
            }}
          >
            {heroData.buttonText}
          </a>
        )}
      </div>
    </section>
  );
};

export default HeroSection;
```

### Vanilla JavaScript Example

```javascript
// Fetch hero section
async function fetchHeroSection() {
  try {
    const response = await fetch(
      'https://your-api-domain.com/api/products/hero-section/'
    );
    const data = await response.json();

    if (data.success && data.heroSection.isActive) {
      renderHeroSection(data.heroSection);
    }
  } catch (error) {
    console.error('Error fetching hero section:', error);
  }
}

function renderHeroSection(heroData) {
  const heroSection = document.getElementById('hero-section');
  if (!heroSection) return;

  // Set background style
  let backgroundStyle = '';

  switch (heroData.backgroundType) {
    case 'image':
      backgroundStyle = `background-image: url(${heroData.imageUrl}); background-size: cover; background-position: center;`;
      break;
    case 'single_color':
      backgroundStyle = `background-color: ${heroData.singleColor};`;
      break;
    case 'gradient':
      const gradient = `linear-gradient(${
        heroData.gradientDirection
      }, ${heroData.gradientColors.join(', ')})`;
      backgroundStyle = `background: ${gradient};`;
      break;
  }

  heroSection.style.cssText = `
    ${backgroundStyle}
    color: ${heroData.textColor};
    min-height: 500px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 2rem;
    position: relative;
  `;

  // Add overlay for images
  if (heroData.backgroundType === 'image') {
    const overlay = document.createElement('div');
    overlay.style.cssText = `
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: rgba(0, 0, 0, 0.4);
      z-index: 1;
    `;
    heroSection.appendChild(overlay);
  }

  // Create content
  const content = document.createElement('div');
  content.style.cssText = 'position: relative; z-index: 2; max-width: 800px;';

  const title = document.createElement('h1');
  title.textContent = heroData.title;
  title.style.cssText = `
    font-size: 3rem;
    font-weight: bold;
    margin-bottom: 1rem;
    color: ${heroData.textColor};
  `;

  content.appendChild(title);

  if (heroData.subtitle) {
    const subtitle = document.createElement('p');
    subtitle.textContent = heroData.subtitle;
    subtitle.style.cssText = `
      font-size: 1.5rem;
      margin-bottom: 2rem;
      color: ${heroData.textColor};
    `;
    content.appendChild(subtitle);
  }

  if (heroData.buttonText && heroData.buttonLink) {
    const button = document.createElement('a');
    button.href = heroData.buttonLink;
    button.textContent = heroData.buttonText;
    button.style.cssText = `
      display: inline-block;
      padding: 1rem 2rem;
      background-color: ${heroData.textColor};
      color: #000;
      text-decoration: none;
      border-radius: 8px;
      font-weight: bold;
    `;
    content.appendChild(button);
  }

  heroSection.appendChild(content);
}

// Call on page load
fetchHeroSection();
```

### HTML Structure

```html
<!DOCTYPE html>
<html>
  <head>
    <title>Homepage</title>
  </head>
  <body>
    <!-- Hero Section Container -->
    <section id="hero-section">
      <!-- Content will be dynamically inserted here -->
    </section>

    <script src="hero-section.js"></script>
  </body>
</html>
```

---

## Admin Panel Integration

### React Admin Component Example

```tsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const HeroSectionAdmin: React.FC = () => {
  const [heroData, setHeroData] = useState<HeroSection | null>(null);
  const [loading, setLoading] = useState(false);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>('');

  useEffect(() => {
    fetchHeroSection();
  }, []);

  const fetchHeroSection = async () => {
    try {
      const response = await axios.get<HeroSectionResponse>(
        '/api/admin/hero-section/',
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('adminToken')}`,
          },
        }
      );

      if (response.data.success) {
        setHeroData(response.data.heroSection);
        if (response.data.heroSection.imageUrl) {
          setPreviewUrl(response.data.heroSection.imageUrl);
        }
      }
    } catch (error) {
      console.error('Error fetching hero section:', error);
    }
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setImageFile(file);

      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewUrl(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const formData = new FormData();

      if (imageFile) {
        formData.append('image', imageFile);
      }

      if (heroData) {
        formData.append('backgroundType', heroData.backgroundType);
        formData.append('title', heroData.title);
        formData.append('subtitle', heroData.subtitle || '');
        formData.append('buttonText', heroData.buttonText || '');
        formData.append('buttonLink', heroData.buttonLink || '');
        formData.append('textColor', heroData.textColor);
        formData.append('singleColor', heroData.singleColor);
        formData.append(
          'gradientColors',
          JSON.stringify(heroData.gradientColors)
        );
        formData.append('gradientDirection', heroData.gradientDirection);
        formData.append('isActive', heroData.isActive.toString());
      }

      const response = await axios.put(
        '/api/admin/hero-section/update/',
        formData,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('adminToken')}`,
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      if (response.data.success) {
        alert('Hero section updated successfully!');
        setHeroData(response.data.heroSection);
      }
    } catch (error: any) {
      alert(error.response?.data?.error || 'Failed to update hero section');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className='hero-section-admin'>
      <h2>Hero Section Management</h2>

      <form onSubmit={handleSubmit}>
        {/* Background Type Selection */}
        <div>
          <label>Background Type:</label>
          <select
            value={heroData?.backgroundType || 'image'}
            onChange={e =>
              setHeroData({
                ...heroData!,
                backgroundType: e.target.value as any,
              })
            }
          >
            <option value='image'>Image</option>
            <option value='single_color'>Single Color</option>
            <option value='gradient'>Gradient</option>
          </select>
        </div>

        {/* Image Upload */}
        {heroData?.backgroundType === 'image' && (
          <div>
            <label>Hero Image:</label>
            <input type='file' accept='image/*' onChange={handleImageChange} />
            {previewUrl && (
              <img
                src={previewUrl}
                alt='Preview'
                style={{ maxWidth: '300px', marginTop: '10px' }}
              />
            )}
          </div>
        )}

        {/* Single Color */}
        {heroData?.backgroundType === 'single_color' && (
          <div>
            <label>Background Color:</label>
            <input
              type='color'
              value={heroData.singleColor}
              onChange={e =>
                setHeroData({
                  ...heroData!,
                  singleColor: e.target.value,
                })
              }
            />
          </div>
        )}

        {/* Gradient Colors */}
        {heroData?.backgroundType === 'gradient' && (
          <div>
            <label>Gradient Colors:</label>
            {heroData.gradientColors.map((color, index) => (
              <input
                key={index}
                type='color'
                value={color}
                onChange={e => {
                  const newColors = [...heroData.gradientColors];
                  newColors[index] = e.target.value;
                  setHeroData({
                    ...heroData!,
                    gradientColors: newColors,
                  });
                }}
              />
            ))}
            <button
              type='button'
              onClick={() =>
                setHeroData({
                  ...heroData!,
                  gradientColors: [...heroData.gradientColors, '#000000'],
                })
              }
            >
              Add Color
            </button>

            <label>Gradient Direction:</label>
            <select
              value={heroData.gradientDirection}
              onChange={e =>
                setHeroData({
                  ...heroData!,
                  gradientDirection: e.target.value,
                })
              }
            >
              <option value='to right'>To Right</option>
              <option value='to bottom'>To Bottom</option>
              <option value='to left'>To Left</option>
              <option value='to top'>To Top</option>
              <option value='135deg'>135deg (Diagonal)</option>
              <option value='45deg'>45deg (Diagonal)</option>
            </select>
          </div>
        )}

        {/* Text Content */}
        <div>
          <label>Title:</label>
          <input
            type='text'
            value={heroData?.title || ''}
            onChange={e =>
              setHeroData({
                ...heroData!,
                title: e.target.value,
              })
            }
            required
          />
        </div>

        <div>
          <label>Subtitle:</label>
          <input
            type='text'
            value={heroData?.subtitle || ''}
            onChange={e =>
              setHeroData({
                ...heroData!,
                subtitle: e.target.value,
              })
            }
          />
        </div>

        <div>
          <label>Button Text:</label>
          <input
            type='text'
            value={heroData?.buttonText || ''}
            onChange={e =>
              setHeroData({
                ...heroData!,
                buttonText: e.target.value,
              })
            }
          />
        </div>

        <div>
          <label>Button Link:</label>
          <input
            type='text'
            value={heroData?.buttonLink || ''}
            onChange={e =>
              setHeroData({
                ...heroData!,
                buttonLink: e.target.value,
              })
            }
          />
        </div>

        <div>
          <label>Text Color:</label>
          <input
            type='color'
            value={heroData?.textColor || '#FFFFFF'}
            onChange={e =>
              setHeroData({
                ...heroData!,
                textColor: e.target.value,
              })
            }
          />
        </div>

        <div>
          <label>
            <input
              type='checkbox'
              checked={heroData?.isActive || false}
              onChange={e =>
                setHeroData({
                  ...heroData!,
                  isActive: e.target.checked,
                })
              }
            />
            Active
          </label>
        </div>

        <button type='submit' disabled={loading}>
          {loading ? 'Saving...' : 'Save Changes'}
        </button>
      </form>
    </div>
  );
};

export default HeroSectionAdmin;
```

---

## CSS Styling Examples

### Basic Hero Section Styles

```css
.hero-section {
  min-height: 500px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 2rem;
  position: relative;
  width: 100%;
}

.hero-section h1 {
  font-size: 3rem;
  font-weight: bold;
  margin-bottom: 1rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.hero-section p {
  font-size: 1.5rem;
  margin-bottom: 2rem;
}

.hero-section .hero-button {
  display: inline-block;
  padding: 1rem 2rem;
  text-decoration: none;
  border-radius: 8px;
  font-weight: bold;
  transition: transform 0.2s, box-shadow 0.2s;
}

.hero-section .hero-button:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

/* Overlay for image backgrounds */
.hero-section.background-image::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.4);
  z-index: 1;
}

.hero-section.background-image > * {
  position: relative;
  z-index: 2;
}

/* Responsive Design */
@media (max-width: 768px) {
  .hero-section {
    min-height: 400px;
    padding: 1rem;
  }

  .hero-section h1 {
    font-size: 2rem;
  }

  .hero-section p {
    font-size: 1.2rem;
  }
}
```

---

## Background Type Examples

### 1. Image Background

```javascript
{
  backgroundType: "image",
  imageUrl: "https://example.com/hero-image.jpg",
  title: "Welcome",
  textColor: "#FFFFFF"
}
```

**CSS Result:** `background-image: url(https://example.com/hero-image.jpg);`

### 2. Single Color Background

```javascript
{
  backgroundType: "single_color",
  singleColor: "#4F46E5",
  title: "Welcome",
  textColor: "#FFFFFF"
}
```

**CSS Result:** `background-color: #4F46E5;`

### 3. Gradient Background

```javascript
{
  backgroundType: "gradient",
  gradientColors: ["#667eea", "#764ba2"],
  gradientDirection: "to right",
  title: "Welcome",
  textColor: "#FFFFFF"
}
```

**CSS Result:** `background: linear-gradient(to right, #667eea, #764ba2);`

---

## Error Handling

```typescript
try {
  const response = await fetch('/api/products/hero-section/');
  const data = await response.json();

  if (!data.success) {
    // Handle error
    console.error('API Error:', data.error);
    // Show default hero or hide hero section
    return;
  }

  if (!data.heroSection.isActive) {
    // Hero section is inactive, don't display
    return;
  }

  // Render hero section
  renderHero(data.heroSection);
} catch (error) {
  console.error('Network error:', error);
  // Show fallback or hide hero section
}
```

---

## Notes

1. **Image Upload**: Maximum file size is 10MB. Supported formats: JPEG, PNG,
   GIF, WEBP
2. **Color Format**: All colors must be in hex format (e.g., `#FF5733`)
3. **Gradient Direction**: Supports CSS gradient directions like `to right`,
   `to bottom`, `135deg`, etc.
4. **Active Status**: Only active hero sections are returned by the public
   endpoint
5. **Default Values**: If no hero section exists, the API returns default values
6. **Caching**: Consider caching the hero section data on the frontend to reduce
   API calls
