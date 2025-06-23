import "./Blockchain.css"
import type { Block } from '../../types/types';

interface BlockchainProperties {
    blocks: Block[]
}

export const formatTimestamp = (isoString: string): string => {
    const date = new Date(isoString);

    const day = date.getDate().toString().padStart(2, '0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0'); // Enero es 0
    const year = date.getFullYear();

    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const seconds = date.getSeconds().toString().padStart(2, '0');

    return `${day}/${month}/${year} ${hours}:${minutes}:${seconds}`;
};

export const Blockchain = ({ blocks }: BlockchainProperties) => (
    <div className="blockchacin-container">
        <h2 className="title">Blockchain</h2>
        {blocks.length === 0 || blocks.length === 1 ? (
            <p className="title">No posee bloques aún</p>
        ) : (
            <table className="blockchain-table">
                <thead>
                    <tr>
                        <th>Block ID</th>
                        <th>Hash</th>
                        <th>Prev Hash</th>
                        <th>Miner</th>
                        <th>Nonce</th>
                        <th>TX ID</th>
                        <th>Source</th>
                        <th>Target</th>
                        <th>Amount</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
                    {blocks.slice(1).map((block) => {
                        const tx = block.transaction;

                        return (
                            <tr key={block.block_id}>
                                <td>{block.block_id}</td>
                                <td>{block.block_hash?.slice(0, 15) ?? 'N/A'}</td>
                                <td>{block.previous_hash?.slice(0, 15) ?? 'N/A'}</td>
                                <td>
                                    {block.miner === "COORDINATOR"
                                        ? "Coordinador"
                                        : block.miner?.slice(0, 4) ?? 'N/A'}
                                </td>
                                <td>{block.nonce}</td>
                                <td>{tx?.tx_id ?? 'N/A'}</td>
                                <td>
                                    {tx?.source === "0000000000"
                                        ? "0000000000"
                                        : tx?.source?.slice(0, 4) ?? 'N/A'}
                                </td>
                                <td>{tx?.target?.slice(0, 4) ?? 'N/A'}</td>
                                <td>{tx?.amount ?? 'N/A'}</td>
                                <td style={{ maxWidth: '60px', wordBreak: 'break-word' }}>
                                    {tx?.description ?? 'N/A'}
                                </td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        )}
    </div>
);

export default Blockchain;
