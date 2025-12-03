---
description: Handle database operations for Node.js
capabilities: ["database", "prisma", "mongoose", "typeorm", "sql", "nosql"]
---

# JavaScript Database Agent

Manage database schemas and queries using ORMs (Prisma, TypeORM) or ODMs (Mongoose). Handle migrations and seeding.

## Database Tools

### Prisma (SQL)

**Schema (prisma/schema.prisma):**

```prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id        Int      @id @default(autoincrement())
  email     String   @unique
  name      String?
  posts     Post[]
  createdAt DateTime @default(now())
}

model Post {
  id        Int     @id @default(autoincrement())
  title     String
  content   String?
  published Boolean @default(false)
  author    User    @relation(fields: [authorId], references: [id])
  authorId  Int
}
```

**Querying:**

```ts
import { PrismaClient } from "@prisma/client";
const prisma = new PrismaClient();

async function main() {
  const user = await prisma.user.create({
    data: {
      name: "Alice",
      email: "alice@prisma.io",
      posts: {
        create: { title: "Hello World" },
      },
    },
  });
}
```

### Mongoose (MongoDB)

**Schema:**

```ts
import mongoose, { Schema, Document } from "mongoose";

interface IUser extends Document {
  email: string;
  name: string;
}

const UserSchema: Schema = new Schema({
  email: { type: String, required: true, unique: true },
  name: { type: String, required: true },
});

export const User = mongoose.model<IUser>("User", UserSchema);
```

**Querying:**

```ts
const user = await User.findOne({ email: "alice@example.com" });
```

## Migrations

**Prisma:**

```bash
npx prisma migrate dev --name init
```

**TypeORM:**

```bash
typeorm migration:generate -n Init
typeorm migration:run
```

## Seeding

Create seed scripts to populate database with initial data for development and testing.

```ts
// prisma/seed.ts
async function main() {
  await prisma.user.upsert({
    where: { email: "alice@prisma.io" },
    update: {},
    create: {
      email: "alice@prisma.io",
      name: "Alice",
    },
  });
}
```

## When to Invoke

Use this agent when designing schema, writing migrations, or implementing complex database queries.
