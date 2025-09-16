// file: prisma/seed.ts
import { PrismaClient } from "@prisma/client"
const prisma = new PrismaClient()
async function main() {
  const u = await prisma.user.upsert({
    where: { email: "demo@example.com" },
    update: {},
    create: { email: "demo@example.com" },
  })
  await prisma.item.create({ data: { title: "Hello Item", ownerId: u.id } })
  console.log("Seeded:", u.email)
}
main().finally(()=>prisma.$disconnect())
