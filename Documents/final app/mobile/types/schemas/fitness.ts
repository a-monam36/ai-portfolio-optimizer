import {z} from 'zod';

export const MusleGroupsEnum = z.enum(['Shoulders', 'Chest', 'Biceps', 'Triceps', 'Back', 'Quads', 'Hamstrings', 'Glutes', 'Calves', 'Core']);

export const MuscleRatingValueSchema = z.number()
    .int()
    .min(1, 'Rating must be atleat 1')
    .max(10, 'rating must be at most 10')

export const MusleRatingSchema = z.object({
    muscle: MusleGroupsEnum, 
    rating: MuscleRatingValueSchema
})


export type MuscleRatingInfer = z.infer<typeof MuscleRatingSchema>;