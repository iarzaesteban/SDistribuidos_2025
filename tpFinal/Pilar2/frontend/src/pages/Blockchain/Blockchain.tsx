import "./Blockchain.css"
import type { Block } from '../../types/types';

interface BlockchainProperties {
    blocks: Block[]
}

export const Blockchain = ({ blocks }: BlockchainProperties) => (
    <div className="blockchacin-container">

        {blocks.slice(1).map((block) => (
            <>
                <h2 className="title">Blockchain</h2>
                <div key={block.block_id} className="data-container">

                    <p><strong>Block ID:</strong> {block.block_id}</p>
                    <p><strong>Hash:</strong> {block.block_hash}</p>
                    <p><strong>Prev Hash:</strong> {block.previous_hash}</p>
                    <p><strong>Miner:</strong> {block.miner}</p>
                    <p><strong>Nonce:</strong> {block.nonce}</p>
                    <div className="transaction-container">
                        <p className="subtitle">Transacción:</p>
                        <p><strong>TX ID:</strong> {block.transaction.tx_id}</p>
                        <p><strong>Source:</strong> {block.transaction.source}</p>
                        <p><strong>Target:</strong> {block.transaction.target}</p>
                        <p><strong>Amount:</strong> {block.transaction.amount}</p>
                        <p><strong>Description:</strong> {block.transaction.description}</p>
                        <p><strong>Timestamp:</strong> {block.transaction.timestamp}</p>
                    </div>
                </div>
            </>
        ))}
    </div>
);

export default Blockchain;
