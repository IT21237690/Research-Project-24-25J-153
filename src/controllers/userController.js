const User = require('../models/User');
const bcrypt = require('bcryptjs');

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
