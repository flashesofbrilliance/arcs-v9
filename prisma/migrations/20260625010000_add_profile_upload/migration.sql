-- CreateTable
CREATE TABLE "ProfileUpload" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "pdfUrl" TEXT,
    "exportUrl" TEXT,
    "skipped" BOOLEAN NOT NULL DEFAULT false,
    "uploadedAt" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "ProfileUpload_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "ProfileUpload_userId_key" ON "ProfileUpload"("userId");

-- AddForeignKey
ALTER TABLE "ProfileUpload" ADD CONSTRAINT "ProfileUpload_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
