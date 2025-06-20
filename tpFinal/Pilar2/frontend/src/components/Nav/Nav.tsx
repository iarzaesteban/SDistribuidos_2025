import { useState } from 'react';
import BlockchainViewer from '../BlockchainViewer';
import './Nav.css';

interface NavProperties {
    handleCreateTask: () => void;
}

const Nav = ({ handleCreateTask }: NavProperties) => {
    const [goToHome, setGoToHome] = useState<boolean>(false);
    return (
        <section className="nav-container">
            <button
                className="button"
                onClick={() => { handleCreateTask(); setGoToHome(true) }}>
                Home
            </button>

            {goToHome && <BlockchainViewer />}
        </section>
    )

};
export default Nav;