export interface Config {
    hash_algorithm: string;
    max_tries_per_tx: number;
    monitoring_window_start: number;
    monitoring_window_end: number;
    publish_window_start: number;
    publish_window_end: number;
    window_period_seconds: number;
}

export interface Transaction {
    tx_id: string;
    source: string;
    target: string;
    amount: number;
    description: string;
    timestamp: string;
    sign: string;
}

export interface TransactionStatus {
    source: string;
    target: string;
    amount: number;
    description: string;
    timestamp: string;
    sign: string;
    tx_id: string;
    tries: number;
    status: string;
    challenge: string;
}

export interface TransactionResponse {
    status: string;
    tx: TransactionStatus;
}

interface Block_name{
    block_name: string;
}

export interface GenesisBlockType {
    block_id: number;
    transaction: Block_name;
    config: Config;
    block_hash: string;
}

export interface Block {
    block_id: number;
    previous_hash: string;
    nonce: number;
    miner: string;
    prefix: string;
    block_hash: string;
    transaction: Transaction;
}

export interface WorkerInfo {
    type: string;
    port: string;
    pub_key: string;
}

export interface Worker {
    ip: string;
    info: WorkerInfo;
}

export interface RegisteredWorkersResponse {
    status: string;
    workers: Worker[];
}

export interface LastBlockChainedType{
    block_id: number;
    previous_hash: string;
    nonce: string;
    miner: string;
    prefix: string;
    block_hash:string;
    transaction: Transaction;
}

export interface InProgressTxResponse {
    last_hash: string;
    transactions: TransactionStatus[];
}

export interface EarringQueueResponse {
    count: number;
    transactions: TransactionStatus[];
}