import React, { useState } from 'react';
import toast, { Toaster } from 'react-hot-toast';
import { ProgressSpinner } from 'primereact/progressspinner';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import 'primereact/resources/themes/saga-blue/theme.css';
import 'primereact/resources/primereact.min.css';
import 'primeicons/primeicons.css';
import "../Assets/Styles/display.css"

const HomePage = () => {
    const routes_object = {
        "/get_by_document_no": "Enter Document Number",
        "/get_by_year": "Enter Year",
        "/search": "Enter Search Query"
    }
    const routes_params = {
        "/get_by_document_no": "document_no",
        "/get_by_year": "year",
        "/search": "word"
    }

    const routes = Object.keys(routes_object);
    const [selectedRoute, setSelectedRoute] = useState('');
    const [parameter, setParameter] = useState('');
    const [isloading, setIsloading] = useState(false)
    const [data, setData] = useState();

    const handleScrapDataClick = () => {
        setIsloading(true)
        fetch('/scrape')
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error('Failed to fetch data');
                }
            })
            .then(data => {
                toast.success(data.message);
                console.log(data.message);
                setIsloading(false);
            })
            .catch(error => {
                console.error(error);
                setIsloading(false);
            });
    };


    const handleApiClick = () => {
        let isvalid;
        setIsloading(true)
        fetch(selectedRoute + "?" + routes_params[selectedRoute] + "=" + parameter)
            .then(response => {
                isvalid = response.ok;
                return response.json();
            })
            .then(data => {
                if (!isvalid) {
                    toast.error(data.message);
                    console.log(data.message);
                    setIsloading(false);
                }
                else {
                    toast.success(data.message);
                    setData(data.result);
                    console.log(data.result);
                    setIsloading(false);
                }
            })
            .catch(error => {
                console.error(error);
                setIsloading(false);
            });
    };

    const header = (
        <div className="d-flex flex-wrap align-items-center justify-content-between gap-2">
            <span className="text-xl text-900 font-bold">Data</span>
            <Button icon="pi pi-refresh" rounded raised onClick={handleApiClick} />
        </div>
    );

    return (
        <>
            <div className="container" style={{ marginTop: "6rem" }}>
                <header className="text-center mt-4">
                    <h1>Propreturns</h1>
                </header>

                <div className="text-center mt-4">
                    <p>Click here to scrape the data</p>
                    <button className="btn btn-primary" onClick={handleScrapDataClick}>
                        {isloading ? <ProgressSpinner style={{ width: '30px', height: '30px' }} /> : "Scrap data"}
                    </button>
                </div>

                <div className="card mt-4">
                    <div className="card-body">
                        <h5 className="card-title">API Request</h5>
                        <div className="d-flex flex-column align-items-center">
                            <select
                                className="form-select mb-2"
                                value={selectedRoute}
                                onChange={(e) => setSelectedRoute(e.target.value)}
                            >
                                <option value="">Select Route</option>
                                {routes.map((route) => (<option value={route}>{route}</option>))}
                            </select>
                            <input
                                type={routes_params[selectedRoute] === "year" ? "number" : "text"}
                                className="form-control mb-2"
                                placeholder={selectedRoute ? routes_object[selectedRoute] : "Enter Parameter"}
                                value={parameter}
                                onChange={(e) => setParameter(e.target.value)}
                            />
                            <button className="btn btn-success mt-2" style={{ width: "20%" }} onClick={handleApiClick}>
                                Call API
                            </button>
                        </div>
                    </div>
                </div>
                <Toaster />
            </div>

            {data && (
                <div className="Display container">
                    {data === undefined ? (
                        <div className="loading-spinner">
                            <p>Loading...</p>
                        </div>
                    ) : (
                        <div className="datatable-demo">
                            <div className="card">
                                <DataTable value={data} header={header} removableSort showGridlines paginator rows={5} rowsPerPageOptions={[5, 10, 25, 50]}>
                                    <Column field="Buyer_name" header="Buyer Name" sortable />
                                    <Column field="Other_information" header="Other Information" />
                                    <Column field="Seller_name" header="Seller Name" sortable />
                                </DataTable>
                            </div>
                        </div>
                    )}
                </div>
            )}

        </>
    );
};

export default HomePage;
