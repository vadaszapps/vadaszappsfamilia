const functions = require('firebase-functions');

exports.kofiWebhook = functions.https.onRequest(async (req, res) => {
    console.log('Kofi webhook fut');
    
    try {
        let data = req.body.data;
        if (!data) {
            return res.status(400).send('No data');
        }
        
        const payment = JSON.parse(data);
        
        // Csak naplózzuk és visszaküldjük a sikeres választ
        console.log('Fizetés:', {
            email: payment.email,
            amount: payment.amount,
            credits: Math.floor(parseFloat(payment.amount) * 10)
        });
        
        // Visszaküldjük, hogy az app feldolgozhassa
        res.status(200).json({
            success: true,
            email: payment.email,
            amount: payment.amount,
            credits: Math.floor(parseFloat(payment.amount) * 10)
        });
        
    } catch (error) {
        console.error('Hiba:', error);
        res.status(500).json({ success: false, error: error.message });
    }
});