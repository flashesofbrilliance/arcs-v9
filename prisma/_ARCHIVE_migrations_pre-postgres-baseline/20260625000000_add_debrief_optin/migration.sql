-- AlterTable
ALTER TABLE "User" ADD COLUMN "firstDebriefSentAt" TIMESTAMP(3);
ALTER TABLE "User" ADD COLUMN "debriefOptIn" BOOLEAN NOT NULL DEFAULT false;
