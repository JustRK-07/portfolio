import { defineCollection, z } from 'astro:content';

const projects = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    year: z.number().int(),
    category: z.enum(['Multi-Agent', 'Fintech', 'Edge-AI', 'Full-Stack', 'RAG']),
    stack: z.array(z.string()).min(1),
    githubUrl: z.string().url().nullable(),
    demoUrl: z.string().url().optional(),
    thumbnail: z.string(),
    featured: z.boolean().default(true),
    summary: z.string(),
    problem: z.string(),
    approach: z.string(),
    results: z.array(z.string()).min(1),
    tech: z.array(z.string()).min(1),
    status: z.enum(['Public', 'Private', 'Coming Soon']).default('Public'),
    coverImage: z.string().optional(),
    architectureDiagram: z.string().optional(),
    images: z.array(z.string()).optional(),
    metrics: z
      .array(
        z.object({
          label: z.string(),
          value: z.string(),
        })
      )
      .optional(),
    role: z.string().optional(),
    caseStudy: z.boolean().default(false),
    sortOrder: z.number().int().optional(),
  }),
});

const experience = defineCollection({
  type: 'content',
  schema: z.object({
    company: z.string(),
    website: z.string().url().optional(),
    role: z.string(),
    period: z.string(),
    location: z.string().optional(),
    summary: z.string(),
    bullets: z.array(z.string()).min(1),
    technologies: z.array(z.string()).min(1),
    sortOrder: z.number().int(),
  }),
});

const patents = defineCollection({
  type: 'data',
  schema: z.object({
    title: z.string(),
    venue: z.string(),
    status: z.enum(['Filed', 'Accepted', 'Published']),
    year: z.number().int(),
    link: z.string().url().optional(),
    description: z.string(),
    sortOrder: z.number().int().optional(),
  }),
});

const achievements = defineCollection({
  type: 'data',
  schema: z.object({
    title: z.string(),
    detail: z.string(),
    year: z.string(),
    rank: z.string().optional(),
    sortOrder: z.number().int().optional(),
  }),
});

const writing = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    publishedAt: z.date(),
    readingTime: z.string().optional(),
    tags: z.array(z.string()),
    draft: z.boolean().default(true),
  }),
});

export const collections = {
  projects,
  experience,
  patents,
  achievements,
  writing,
};
