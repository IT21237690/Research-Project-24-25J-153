const User = require('../models/User');
const bcrypt = require('bcryptjs');

const QA = require('../models/QA');
// const Pronunciation = require('../models/Pronunciation');
// const Image = require('../models/Image');
// const Text = require('../models/Text');

// Get all users (Admin only)
exports.getAllUsers = async (req, res) => {
    try {
        if (req.user.role !== 'admin') {
            return res.status(403).json({ msg: "Access denied. Admins only." });
        }
        const users = await User.find().select('-password');
        res.json(users);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};

// Get user by ID
exports.getUserById = async (req, res) => {
    try {
        const user = await User.findById(req.params.id).select('-password');
        if (!user) return res.status(404).json({ msg: "User not found" });
        res.json(user);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};

// Update user
exports.updateUser = async (req, res) => {
    try {
        const { name, email, password, role } = req.body;
        let user = await User.findById(req.params.id);

        if (!user) return res.status(404).json({ msg: "User not found" });

        if (password) {
            user.password = await bcrypt.hash(password, 10);
        }
        if (name) user.name = name;
        if (email) user.email = email;
        if (role && req.user.role === 'admin') user.role = role; // Only admin can update roles

        await user.save();
        res.json({ msg: "User updated successfully", user });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};

// Delete user (Admin only)
exports.deleteUser = async (req, res) => {
    try {
        if (req.user.role !== 'admin') {
            return res.status(403).json({ msg: "Access denied. Admins only." });
        }

        const user = await User.findById(req.params.id);
        if (!user) return res.status(404).json({ msg: "User not found" });

        await user.remove();
        res.json({ msg: "User deleted successfully" });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};


exports.getUserResults = async (req, res) => {
    try {
        let user_id = req.user.id;

        console.log("Extracted user_id from token:", user_id);
        console.log("Type of user_id:", typeof user_id);

        // DO NOT Convert user_id to ObjectId since it's stored as a string
        const qaResults = await QA.find({ user_id: user_id });
        // const pronunciationResults = await Pronunciation.find({ user_id: user_id });
        // const imageResults = await Image.find({ user_id: user_id });
        // const textResults = await Text.find({ user_id: user_id });

        res.json({
            user_id,
            results: {
                QA: qaResults,
                // pronunciation: pronunciationResults,
                // image: imageResults,
                // text: textResults
            }
        });

    } catch (err) {
        console.error("Error in getUserResults:", err.message);
        res.status(500).json({ error: err.message });
    }
};

