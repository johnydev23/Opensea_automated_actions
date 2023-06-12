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

const filePath = 'collection_info.json';
const jsonData = fs.readFileSync(filePath, 'utf8');
const collectionInfo = JSON.parse(jsonData);

for (let i = 0; i < collectionInfo.length; i++) {
    const message = collectionInfo[i].typed_message;
    const signature = signTypedMessage(message);
    collectionInfo[i].signature = signature;
}

const updatedJsonData = JSON.stringify(collectionInfo, null, 2);
fs.writeFileSync(filePath, updatedJsonData);