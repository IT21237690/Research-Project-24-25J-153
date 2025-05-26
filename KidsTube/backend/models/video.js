const mongoose = require("mongoose")

const videoSchema = new mongoose.Schema({
  videoId: {
    type: String,
    required: true,
    unique: true,
  },
  title: {
    type: String,
    required: true,
  },
  description: String,
  thumbnailUrl: String,
  channelId: String,
  channelTitle: String,
  publishedAt: Date,
  tags: [String],
  category: String,
  duration: String,
  viewCount: Number,
  likeCount: Number,
  ageRange: {
    min: Number,
    max: Number,
  },
  educationalValue: {
    type: Number,
    min: 1,
    max: 5,
  },
  entertainmentValue: {
    type: Number,
    min: 1,
    max: 5,
  },
  createdAt: {
    type: Date,
    default: Date.now,
  },
})

module.exports = mongoose.model("Video", videoSchema)

// Create a test video if none exist
const createTestVideo = async () => {
  try {
    const count = await mongoose.model('Video').countDocuments();
    if (count === 0) {
      console.log('Creating test video');
      const testVideo = new mongoose.model('Video')({
        videoId: 'dQw4w9WgXcQ',
        title: 'Test Kids Video',
        description: 'This is a test video for kids',
        thumbnailUrl: 'https://i.ytimg.com/vi/dQw4w9WgXcQ/mqdefault.jpg',
        channelId: 'test-channel',
        channelTitle: 'Kids Channel',
        publishedAt: new Date(),
        tags: ['kids', 'test', 'educational'],
        category: 'Education',
        viewCount: 1000
      });
      await testVideo.save();
      console.log('Test video created');
    }
  } catch (error) {
    console.error('Error creating test video:', error);
  }
};

createTestVideo();

