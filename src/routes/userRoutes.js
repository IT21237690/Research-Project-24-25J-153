const express = require('express');
const { getAllUsers, getUserById, updateUser, deleteUser,getUserResults } = require('../controllers/userController');
const authMiddleware = require('../middleware/authMiddleware');

const router = express.Router();

router.get('/', authMiddleware, getAllUsers); // Admin only
router.get('/results', authMiddleware, getUserResults);
router.get('/details', authMiddleware, getUserById);
router.put('/:id', authMiddleware, updateUser);
router.delete('/:id', authMiddleware, deleteUser); // Admin only


module.exports = router;
