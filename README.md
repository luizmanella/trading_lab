<h1> README</h1>
<h3>Summary:</h3>
<p>This repo contains a working sample of the simulator I developed for Algo-nomics. This version is only capable of running simulations over daily strategies for Equity and ETF assets. The skeleton is built to introduce various other assets (i.e., options, futures, options on futures) but in this sample version they are not there.</p>
<p>To run this one needs their own database of securities and would need to write code to interact with that database. That code would go inside the <i>model.py</i> file under the <i>pull_data</i> method. You would need to pull the data for the current date, and additionally for some historical dates as well which is decided by the <i>look_back</i> parameter; the <i>columns</i> parameter was made to pre-filter out columns from the database that were not desired for a specific model.</p>
<p>Other than updating the method to work with your personal database or securities, there are two base test files to use. First is the <i>test_model</i>. It provides a dummy model for your strategy and how it should behave generally. Different model ideas would be developed into this structure to function with the rest of the code. The second file you would use is the <i>testing_code.py</i> which handles initializing the simulator, setting relevant parameters, setting the model and running the simulation.</p>
<h3>Warnings</h3>:
<ul>
    <li>
        Certain variables and ideas that make this more realistic are not live in this version. This includes
        <ul>
            <li>set_broker in testing_code.py (ideally sets in place commission and other things)</li>
            <li>computing result statistics</li>
        </ul>
    </li>
</ul>