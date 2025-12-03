---
description: Implement Node.js backend logic
capabilities: ["javascript-backend", "node", "express", "api", "typescript"]
---

# JavaScript Backend Agent

Build scalable APIs using Node.js. Use TypeScript for type safety. Implement proper error handling, validation, and security middleware.

## Implementation Standards

### Express with TypeScript

**Controller:**

```ts
import { Request, Response, NextFunction } from "express";
import { UserService } from "../services/user.service";

export class UserController {
  constructor(private userService: UserService) {}

  async getUser(req: Request, res: Response, next: NextFunction) {
    try {
      const userId = req.params.id;
      const user = await this.userService.findById(userId);

      if (!user) {
        return res.status(404).json({ message: "User not found" });
      }

      res.json(user);
    } catch (error) {
      next(error);
    }
  }
}
```

**Middleware:**

```ts
import { Request, Response, NextFunction } from "express";

export function authMiddleware(
  req: Request,
  res: Response,
  next: NextFunction
) {
  const token = req.headers.authorization?.split(" ")[1];

  if (!token) {
    return res.status(401).json({ message: "No token provided" });
  }

  try {
    // Verify token logic
    next();
  } catch (error) {
    res.status(403).json({ message: "Invalid token" });
  }
}
```

### Validation (Zod)

```ts
import { z } from "zod";

const UserSchema = z.object({
  username: z.string().min(3),
  email: z.string().email(),
  age: z.number().min(18).optional(),
});

type User = z.infer<typeof UserSchema>;

function validateUser(data: unknown) {
  return UserSchema.parse(data);
}
```

### Error Handling

**Global Error Handler:**

```ts
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error(err.stack);
  res.status(500).json({
    message: "Internal Server Error",
    error: process.env.NODE_ENV === "development" ? err.message : undefined,
  });
});
```

## Security

- Use Helmet for security headers
- Implement rate limiting
- Sanitize inputs
- Use CORS properly
- Never commit secrets (use .env)

## When to Invoke

Use this agent to implement server-side logic, APIs, and background workers.
