# Astro CMS Compatibility Guide

## Overview

**YES!** The Portfolio Generator is now fully compatible with Astro CMS through native Astro project generation.

## What is Astro?

Astro is a modern static site generator that:
- Uses component-based architecture (.astro files)
- Provides excellent performance with "Islands Architecture"
- Supports multiple UI frameworks (React, Vue, Svelte, etc.)
- Has built-in content management via Content Collections
- Generates optimized static HTML by default

## How It Works

The Portfolio Generator can now generate **two types of portfolios**:

1. **Static HTML** (Default) - Traditional HTML/CSS site with Decap CMS
2. **Astro Project** (New!) - Modern Astro-based project with full dev environment

## Generating Astro Portfolios

### Via Command Line

```bash
# Generate Astro portfolio
python generate_portfolio.py --input user_data.json --output-dir my-astro-portfolio --astro

# With specific template and theme
python generate_portfolio.py \
  --input user_data.json \
  --output-dir my-astro-portfolio \
  --astro \
  --site-template hybrid \
  --design-theme modern
```

### Via API

```python
import requests

response = requests.post('http://localhost:5000/api/generate-astro', json={
    "user_id": "user-123",
    "basics": {
        "name": "John Doe",
        "summary": "Full-stack developer"
    },
    "projects": [...],
    "site_template": "hybrid",
    "design_theme": "modern"
})

result = response.json()
print(f"Astro project created at: {result['portfolio_path']}")
print(f"Run: {result['dev_command']}")
```

### Via Python API

```python
from generate_portfolio import generate_astro_portfolio

result = generate_astro_portfolio(
    user_data={
        "name": "John Doe",
        "bio": "Developer",
        "projects": [...]
    },
    output_dir="my-astro-portfolio",
    site_template="hybrid",
    design_theme="modern"
)

print(f"Generated at: {result['path']}")
print(f"Dev command: {result['dev_command']}")
```

## Generated Astro Project Structure

```
my-astro-portfolio/
├── package.json           # Astro dependencies
├── astro.config.mjs       # Astro configuration
├── README.md              # Project documentation
├── .gitignore             # Git ignore file
├── src/
│   ├── layouts/
│   │   └── Layout.astro   # Main layout component
│   ├── pages/
│   │   └── index.astro    # Homepage (uses Layout)
│   └── content/
│       └── portfolio/
│           └── data.json  # Your portfolio data
└── public/
    └── styles/
        └── main.css       # Your selected theme CSS
```

## Working with the Generated Project

### 1. Install Dependencies

```bash
cd my-astro-portfolio
npm install
```

### 2. Run Development Server

```bash
npm run dev
```

Visit `http://localhost:4321` to see your portfolio!

### 3. Build for Production

```bash
npm run build
```

The production-ready site will be in `./dist/`

### 4. Preview Production Build

```bash
npm run preview
```

## Editing Your Portfolio Content

### Option 1: Edit JSON Data File

The easiest way to update your portfolio is to edit the JSON file:

```bash
# Edit this file
src/content/portfolio/data.json
```

The file structure:
```json
{
  "name": "Your Name",
  "bio": "Your bio",
  "headline": "Your title",
  "photo_url": "https://...",
  "contact_line": "email | phone",
  "address_line": "Your address",
  "profiles": [
    {"network": "LinkedIn", "url": "https://..."}
  ],
  "skills": ["JavaScript", "Python"],
  "education": [...],
  "projects": [...]
}
```

After editing, the dev server will automatically reload!

### Option 2: Use Astro Studio (Content Management)

Astro provides [Astro Studio](https://studio.astro.build/) for content management:

1. Sign up for Astro Studio
2. Connect your project: `npx astro login`
3. Link your project: `npx astro link`
4. Manage content via the web UI

### Option 3: Integrate with Headless CMS

Astro works great with headless CMS solutions:

- **Contentful**
- **Sanity**
- **Strapi**
- **Payload CMS**
- **Decap CMS** (formerly Netlify CMS)

See [Astro CMS Guides](https://docs.astro.build/en/guides/cms/) for integration details.

## Customizing Your Astro Portfolio

### Modify the Layout

Edit `src/layouts/Layout.astro` to change the structure:

```astro
---
// Add new sections, modify styling, etc.
const { title, portfolio } = Astro.props;
---

<!DOCTYPE html>
<html lang="fr">
<head>
    <title>{title}</title>
    <!-- Add your custom meta tags, scripts, etc. -->
</head>
<body>
    <!-- Customize your layout here -->
</body>
</html>
```

### Add New Pages

Create new `.astro` files in `src/pages/`:

```astro
---
// src/pages/about.astro
import Layout from '../layouts/Layout.astro';
import portfolioData from '../content/portfolio/data.json';
---

<Layout title="About" portfolio={portfolioData}>
    <h1>About Me</h1>
    <p>More details about my work...</p>
</Layout>
```

### Change Styles

The CSS is in `public/styles/main.css`. You can:
- Modify existing styles
- Add new CSS files
- Use Tailwind CSS
- Use CSS-in-JS solutions

### Use UI Components

Astro supports multiple UI frameworks. Add React, Vue, or Svelte:

```bash
# Add React support
npx astro add react

# Add Tailwind CSS
npx astro add tailwind
```

## Deployment Options

### Option 1: Netlify

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod
```

### Option 2: Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

### Option 3: Cloudflare Pages

```bash
npm run build
# Upload ./dist to Cloudflare Pages
```

### Option 4: GitHub Pages

Add to `astro.config.mjs`:
```javascript
export default defineConfig({
  site: 'https://yourusername.github.io',
  base: '/your-repo-name'
});
```

Then deploy via GitHub Actions.

## Comparison: Static HTML vs Astro

| Feature | Static HTML | Astro |
|---------|-------------|-------|
| **Setup** | None needed | npm install |
| **Dev Server** | Simple HTTP server | Astro dev server |
| **Build Process** | None | npm run build |
| **Hot Reload** | No | Yes |
| **Components** | No | Yes (.astro) |
| **Modern JS** | Limited | Full ES6+ support |
| **Frameworks** | No | React, Vue, Svelte |
| **Performance** | Excellent | Excellent |
| **CMS Options** | Decap CMS | Multiple options |
| **Customization** | HTML/CSS editing | Component-based |
| **Best For** | Simple sites | Modern development |

## When to Use Astro

**Choose Astro when you want:**
- ✅ Modern development experience
- ✅ Component-based architecture
- ✅ Hot module replacement (HMR)
- ✅ TypeScript support
- ✅ Integration with React/Vue/Svelte
- ✅ Advanced customization
- ✅ Modern build tooling

**Choose Static HTML when you want:**
- ✅ Zero build step
- ✅ Maximum simplicity
- ✅ Instant deployment
- ✅ No dependencies
- ✅ Traditional workflow

## Migrating Between Formats

### From Static HTML to Astro

```bash
# Generate Astro version
python generate_portfolio.py --input your_data.json --output-dir astro-portfolio --astro
```

### From Astro to Static HTML

```bash
# Generate static version
python generate_portfolio.py --input your_data.json --output-dir static-portfolio
```

Your data stays in JSON format, making it easy to regenerate in either format!

## Advanced: Astro Content Collections

For advanced content management, convert to Astro Content Collections:

1. **Create collection schema** (`src/content/config.ts`):

```typescript
import { defineCollection, z } from 'astro:content';

const portfolioCollection = defineCollection({
  type: 'data',
  schema: z.object({
    name: z.string(),
    bio: z.string(),
    projects: z.array(z.object({
      title: z.string(),
      description: z.string(),
      image: z.string().optional()
    }))
  })
});

export const collections = {
  portfolio: portfolioCollection
};
```

2. **Use in pages**:

```astro
---
import { getEntry } from 'astro:content';
const portfolio = await getEntry('portfolio', 'data');
---
```

## Troubleshooting

### "Module not found" Error

```bash
# Make sure you installed dependencies
npm install
```

### Port Already in Use

```bash
# Use different port
npm run dev -- --port 3000
```

### Build Fails

```bash
# Clear cache
rm -rf node_modules .astro
npm install
npm run build
```

## Resources

- [Astro Documentation](https://docs.astro.build/)
- [Astro Content Collections](https://docs.astro.build/en/guides/content-collections/)
- [Astro CMS Integration](https://docs.astro.build/en/guides/cms/)
- [Astro Discord Community](https://astro.build/chat)

## API Reference

### REST API Endpoint

**Endpoint:** `POST /api/generate-astro`

**Request:**
```json
{
  "user_id": "user-123",
  "basics": {
    "name": "John Doe",
    "summary": "Developer"
  },
  "projects": [...],
  "site_template": "hybrid",
  "design_theme": "modern"
}
```

**Response:**
```json
{
  "success": true,
  "portfolio_id": "abc-123",
  "portfolio_path": "/path/to/project",
  "type": "astro",
  "dev_command": "npm install && npm run dev",
  "build_command": "npm run build",
  "status": "generated"
}
```

## Support

For questions or issues:
- GitHub Issues: https://github.com/pcx-wave/portfolio-generator/issues
- This documentation
- Astro Discord for Astro-specific questions

## License

Same as the main portfolio-generator project (MIT).
