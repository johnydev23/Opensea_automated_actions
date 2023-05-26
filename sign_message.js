const fs = require('fs');
const sigUtil = require('eth-sig-util');
const ethUtil = require('ethereumjs-util');

function signTypedMessage(message) {
    if (message === null){
        return null;
    }
    const privateKeyOrigin = process.env.PRIVATE_KEY;
    const privateKey = ethUtil.toBuffer('0x' + privateKeyOrigin);
    const messageHash = sigUtil.TypedDataUtils.sign(message);
    const sig = ethUtil.ecsign(messageHash, privateKey);
    const serializedSig = ethUtil.bufferToHex(sigUtil.concatSig(sig.v, sig.r, sig.s));
    return serializedSig;
}

fs.readFile('message_list.json', 'utf8', (err, data) => {
    if (err) {
        console.error('Error reading input file:', err);
        return;
    }

    try {
        const messages = JSON.parse(data);

        const signedMessages = messages.map((message) => {
            const signature = signTypedMessage(message);
            return [message, signature];
        });

        const signedMessagesJSON = JSON.stringify(signedMessages);

        fs.writeFile('sign_message_list.json', signedMessagesJSON, 'utf8', (err) => {
            if (err) {
                console.error('Error writing output file:', err);
                return;
            }
        });
    } catch (err) {
        console.error('Error parsing input JSON:', err);
    }
});