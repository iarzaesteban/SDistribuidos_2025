import Header from '../components/Header/Header';
import BlockchainViewer from '../components/BlockchainViewer';
import "./Home.css"
import { Statistics } from '../components/Statistics/Statistics';

const Home = () => (
    <div className="container">
        <Header />
        <Statistics />
        <BlockchainViewer />
    </div>
);

export default Home;
