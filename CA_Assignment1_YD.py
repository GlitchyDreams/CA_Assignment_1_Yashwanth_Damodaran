"""
@author: yashwanth damodaran
"""

#importing the required modules and specific packages
import sys
import pandapower as pp
import pandapower.networks
import pandapower.topology
import pandapower.plotting
import pandapower.converter
import pandapower.estimation
import pandapower.plotting 
import xml.etree.ElementTree as ET
import pandapower.plotting.to_html as html_output
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap

#This parts creates a PyQt5 GUI with a background image and buttons to import EQ and SSH files and to run the model

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Assignment 1")

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Load Background Image
        pixmap = QPixmap('Background.png')
        self.bg_label = QLabel(self)
        self.bg_label.setPixmap(pixmap)
        layout.addWidget(self.bg_label)

        # Insert File Buttons
        self.button_EQ = QPushButton("Import EQ File", self)
        self.button_EQ.clicked.connect(self.EQ_file)
        layout.addWidget(self.button_EQ)

        self.button_SSH = QPushButton("Import SSH File", self)
        self.button_SSH.clicked.connect(self.SSH_file)
        layout.addWidget(self.button_SSH)

        # Run Button
        self.button_Run = QPushButton("Run", self)
        self.button_Run.clicked.connect(self.run_model)
        layout.addWidget(self.button_Run)

    def EQ_file(self):
        EQ_file, _ = QFileDialog.getOpenFileName(self, 'Open EQ File')
        self.EQ_file_XML = EQ_file
        self.Message_EQ = "Successfully added EQ File"

    def SSH_file(self):
        SSH_file, _ = QFileDialog.getOpenFileName(self, 'Open SSH File')
        self.SSH_file_XML = SSH_file
        self.Message_SSH = "Successfully added SSH File"

#This is the main part of the code
    def run_model(self):
        
        
        #This is the XML Parsing and data collection part
        
        tree_EQ = ET.parse(self.EQ_file_XML)
        tree_SSH = ET.parse(self.SSH_file_XML)
        # tree_EQ=ET.parse("MicroGridTestConfiguration_T1_BE_EQ_V2.xml")
        # tree_SSH=ET.parse("MicroGridTestConfiguration_T1_BE_SSH_V2.xml")

        root_EQ = tree_EQ.getroot()
        root_SSH = tree_SSH.getroot()
        cim = "{http://iec.ch/TC57/2013/CIM-schema-cim16#}"
        md = "{http://iec.ch/TC57/61970-552/ModelDescription/1#}"
        rdf = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"


        # The required dictionaries are created to store data
        ac_line_segments_dict = {}
        base_voltage_dict = {}
        breaker_dict = {}
        busbar_section_dict = {}
        connectivity_node_dict = {}
        current_limit_dict = {}
        curve_data_dict = {}
        energy_consumer_dict = {}
        generating_unit_dict = {}
        geographical_region_dict = {}
        line_dict = {}
        linear_shunt_compensator_dict = {}
        load_response_characteristic_dict = {}
        operational_limit_set_dict = {}
        operational_limit_type_dict = {}
        petersen_coil_dict = {}
        phase_tap_changer_asymmetrical_dict = {}
        power_transformer_dict = {}
        power_transformer_end_dict = {}
        ratio_tap_changer_dict = {}
        regulating_control_dict = {}
        substation_dict = {}
        synchronous_machine_dict = {}
        tap_changer_control_dict = {}
        terminal_dict = {}
        voltage_level_dict = {}

        # Loop through 'ACLineSegment' elements and extract data
        for ac_segment_xml in root_EQ.iter(cim + 'ACLineSegment'):
            ac_id = ac_segment_xml.get(rdf + 'ID')
            ac_line_segments_dict[ac_id] = {
                'ID': ac_id,
                'name': ac_segment_xml.find(cim + 'IdentifiedObject.name').text,
                'equipment_container': ac_segment_xml.find(cim + 'Equipment.EquipmentContainer').get(rdf + 'resource'),
                'r': ac_segment_xml.find(cim + 'ACLineSegment.r').text,
                'x': ac_segment_xml.find(cim + 'ACLineSegment.x').text,
                'bch': ac_segment_xml.find(cim + 'ACLineSegment.bch').text,
                'length': ac_segment_xml.find(cim + 'Conductor.length').text,
                'gch': ac_segment_xml.find(cim + 'ACLineSegment.gch').text,
                'base_voltage': ac_segment_xml.find(cim + 'ConductingEquipment.BaseVoltage').get(rdf + 'resource'),
                'r0': ac_segment_xml.find(cim + "ACLineSegment.r0").text,
                'x0': ac_segment_xml.find(cim + "ACLineSegment.x0").text,
                'b0ch': ac_segment_xml.find(cim + "ACLineSegment.b0ch").text,
                'g0ch': ac_segment_xml.find(cim + "ACLineSegment.g0ch").text
            }   
        # print(ac_line_segments)


        # Loop through 'BaseVoltage' elements and extract data
        for base_voltage_xml in root_EQ.iter(cim + "BaseVoltage"):
            base_voltage_id = base_voltage_xml.get(rdf + "ID")
            base_voltage_dict[base_voltage_id] = {
                'ID': base_voltage_id,
                'nominal_voltage': base_voltage_xml.find(cim + "BaseVoltage.nominalVoltage").text
            }

        # print(base_voltage_dict)
        
        # Loop through 'Breaker' elements and extract data
        for breaker_xml in root_EQ.iter(cim + 'Breaker'):
            breaker_id = breaker_xml.get(rdf + 'ID')
            breaker_dict[breaker_id] = {
                'ID': breaker_id,
                'name': breaker_xml.find(cim + 'IdentifiedObject.name').text,
                'equipment_container': breaker_xml.find(cim + 'Equipment.EquipmentContainer').get(rdf + 'resource'),
                'status': " "
            }

        # Loop through 'Breaker' elements in SSH data and update the status in the breaker_dict
        for breaker_xml in root_SSH.iter(cim + "Breaker"):
            breaker_id = breaker_xml.get(rdf + 'about').replace("#", "")
            if breaker_id in breaker_dict:
                breaker_dict[breaker_id]['status'] = breaker_xml.find(cim + "Switch.open").text
        #print(breaker_dict)       

        # Loop through 'BusbarSection' elements and extract data
        for busbar_section_xml in root_EQ.iter(cim + 'BusbarSection'):
            busbar_section_id = busbar_section_xml.get(rdf + 'ID')
            busbar_section_dict[busbar_section_id] = {
                'ID': busbar_section_id,
                'name': busbar_section_xml.find(cim + 'IdentifiedObject.name').text,
                'equipment_container': busbar_section_xml.find(cim + 'Equipment.EquipmentContainer').get(rdf + 'resource')
            }
        
        # print(busbar_section_dict)
        
        # Loop through 'ConnectivityNode' elements and extract data
        for connectivity_node_xml in root_EQ.iter(cim + 'ConnectivityNode'):
            connectivity_node_id = connectivity_node_xml.get(rdf + 'ID')
            connectivity_node_dict[connectivity_node_id] = {
                'ID': connectivity_node_id,
                'name': connectivity_node_xml.find(cim + 'IdentifiedObject.name').text,
                'connectivity_node_container': connectivity_node_xml.find(cim + "ConnectivityNode.ConnectivityNodeContainer").get(rdf + "resource")
            }
        # print(connectivity_node_dict)

        # Loop through 'CurrentLimit' elements and extract data
        for current_limit_xml in root_EQ.iter(cim + "CurrentLimit"):
            current_limit_id = current_limit_xml.get(rdf + "ID")
            current_limit_dict[current_limit_id] = {
                'ID': current_limit_id,
                'name': current_limit_xml.find(cim + "IdentifiedObject.name").text,
                'value': current_limit_xml.find(cim + "CurrentLimit.value").text,
                'operational_limit_set': current_limit_xml.find(cim + "OperationalLimit.OperationalLimitSet").get(rdf + "resource"),
                'operational_limit_type': current_limit_xml.find(cim + "OperationalLimit.OperationalLimitType").get(rdf + "resource")
            }
        # print(current_limit_dict)

        # Loop through 'CurveData' elements and extract data
        for curve_data_xml in root_EQ.iter(cim + "CurveData"):
            curve_data_id = curve_data_xml.get(rdf + "ID")
            curve_data_dict[curve_data_id] = {
                'ID': curve_data_id,
                'xvalue': curve_data_xml.find(cim + "CurveData.xvalue").text,
                'y1value': curve_data_xml.find(cim + "CurveData.y1value").text,
                'y2value': curve_data_xml.find(cim + "CurveData.y2value").text,
                'curve': curve_data_xml.find(cim + "CurveData.Curve").get(rdf + "resource")
            }

        # print(curve_data_dict)

        for energy_consumer_xml in root_EQ.iter(cim + 'EnergyConsumer'):
            energy_consumer_id = energy_consumer_xml.get(rdf + 'ID')
            energy_consumer_dict[energy_consumer_id] = {
                'ID': energy_consumer_id,
                'name': energy_consumer_xml.find(cim + 'IdentifiedObject.name').text,
                'equipment_container': energy_consumer_xml.find(cim + 'Equipment.EquipmentContainer').get(rdf + 'resource'),
                'active_power': "",
                'reactive_power': ""
            }
            
        for energy_consumer_xml in root_SSH.iter(cim + "EnergyConsumer"):
            energy_consumer_id = energy_consumer_xml.get(rdf + 'about').replace("#", "")
            energy_consumer_dict[energy_consumer_id]['active_power'] = energy_consumer_xml.find(cim + "EnergyConsumer.p").text
            energy_consumer_dict[energy_consumer_id]['reactive_power'] = energy_consumer_xml.find(cim + "EnergyConsumer.q").text

        
        #print(energy_consumer_dict)

        # Loop through 'GeneratingUnit' elements and extract data
        for generating_unit_xml in root_EQ.iter(cim + 'GeneratingUnit'):
            generating_unit_id = generating_unit_xml.get(rdf + 'ID')
            generating_unit_dict[generating_unit_id] = {
                'ID': generating_unit_id,
                'name': generating_unit_xml.find(cim + 'IdentifiedObject.name').text,
                'initial_p': generating_unit_xml.find(cim + "GeneratingUnit.initialP").text,
                'nominal_p': generating_unit_xml.find(cim + "GeneratingUnit.nominalP").text,
                'max_operating_p': generating_unit_xml.find(cim + 'GeneratingUnit.maxOperatingP').text,
                'min_operating_p': generating_unit_xml.find(cim + 'GeneratingUnit.minOperatingP').text,
                'gen_control_source': generating_unit_xml.find(cim + "GeneratingUnit.genControlSource").get(rdf + "resource"),
                'equipment_container': generating_unit_xml.find(cim + 'Equipment.EquipmentContainer').get(rdf + 'resource')
            }
        # print(generating_unit_dict)

        # Loop through 'GeographicalRegion' elements and extract data
        for geographical_region_xml in root_EQ.iter(cim + 'GeographicalRegion'):
            geographical_region_id = geographical_region_xml.get(rdf + 'ID')
            geographical_region_dict[geographical_region_id] = {
                'ID': geographical_region_id,
                'name': geographical_region_xml.find(cim + 'IdentifiedObject.name').text
            }
        # print(geographical_region_dict)

        # Loop through 'Line' elements and extract data
        for line_xml in root_EQ.iter(cim + 'Line'):
            line_id = line_xml.get(rdf + 'ID')
            line_dict[line_id] = {
                'ID': line_id,
                'name': line_xml.find(cim + 'IdentifiedObject.name').text,
                'region': line_xml.find(cim + 'Line.Region').get(rdf + 'resource')
            }

        # print(line_dict)

        # Loop through 'LinearShuntCompensator' elements and extract data
        for linear_shunt_compensator_xml in root_EQ.iter(cim + 'LinearShuntCompensator'):
            linear_shunt_compensator_id = linear_shunt_compensator_xml.get(rdf + 'ID')
            linear_shunt_compensator_dict[linear_shunt_compensator_id] = {
                'ID': linear_shunt_compensator_id,
                'name': linear_shunt_compensator_xml.find(cim + 'IdentifiedObject.name').text,
                'b_per_section': linear_shunt_compensator_xml.find(cim + 'LinearShuntCompensator.bPerSection').text,
                'g_per_section': linear_shunt_compensator_xml.find(cim + 'LinearShuntCompensator.gPerSection').text,
                'b0_per_section': linear_shunt_compensator_xml.find(cim + 'LinearShuntCompensator.b0PerSection').text,
                'g0_per_section': linear_shunt_compensator_xml.find(cim + 'LinearShuntCompensator.g0PerSection').text,
                'nom_u': linear_shunt_compensator_xml.find(cim + 'ShuntCompensator.nomU').text,
                'regulating_control': linear_shunt_compensator_xml.find(cim + 'RegulatingCondEq.RegulatingControl').get(rdf + 'resource'),
                'equipment_container': linear_shunt_compensator_xml.find(cim + 'Equipment.EquipmentContainer').get(rdf + 'resource'),
                'q_mvar_sh': ''
            }

        # Loop through 'LoadResponseCharacteristic' elements and extract data
        for load_response_characteristic_xml in root_EQ.iter(cim + 'LoadResponseCharacteristic'):
            load_response_characteristic_id = load_response_characteristic_xml.get(rdf + 'ID')
            load_response_characteristic_dict[load_response_characteristic_id] = {
                'ID': load_response_characteristic_id,
                'name': load_response_characteristic_xml.find(cim + 'IdentifiedObject.name').text,
                'p_constant_current': load_response_characteristic_xml.find(cim + 'LoadResponseCharacteristic.pConstantCurrent').text,
                'p_constant_impedance': load_response_characteristic_xml.find(cim + 'LoadResponseCharacteristic.pConstantImpedance').text,
                'p_constant_power': load_response_characteristic_xml.find(cim + 'LoadResponseCharacteristic.pConstantPower').text,
                'p_frequency_exponent': load_response_characteristic_xml.find(cim + 'LoadResponseCharacteristic.pFrequencyExponent').text,
                'q_constant_current': load_response_characteristic_xml.find(cim + 'LoadResponseCharacteristic.qConstantCurrent').text,
                'q_constant_impedance': load_response_characteristic_xml.find(cim + 'LoadResponseCharacteristic.qConstantImpedance').text,
                'q_constant_power': load_response_characteristic_xml.find(cim + 'LoadResponseCharacteristic.qConstantPower').text,
                'p_voltage_exponent': load_response_characteristic_xml.find(cim + 'LoadResponseCharacteristic.pVoltageExponent').text,
                'q_frequency_exponent': load_response_characteristic_xml.find(cim + 'LoadResponseCharacteristic.qFrequencyExponent').text,
                'q_voltage_exponent': load_response_characteristic_xml.find(cim + 'LoadResponseCharacteristic.qVoltageExponent').text
            }

        # Loop through 'PetersenCoil' elements and extract data
        for petersen_coil_xml in root_EQ.iter(cim + 'PetersenCoil'):
            petersen_coil_id = petersen_coil_xml.get(rdf + 'ID')
            petersen_coil_dict[petersen_coil_id] = {
                'ID': petersen_coil_id,
                'name': petersen_coil_xml.find(cim + 'IdentifiedObject.name').text,
                'equipment_container': petersen_coil_xml.find(cim + 'Equipment.EquipmentContainer').get(rdf + 'resource'),
                'x_ground_nominal': petersen_coil_xml.find(cim + 'PetersenCoil.xGroundNominal').text,
                'x_ground_max': petersen_coil_xml.find(cim + 'PetersenCoil.xGroundMax').text,
                'x_ground_min': petersen_coil_xml.find(cim + 'PetersenCoil.xGroundMin').text,
                'position_current': petersen_coil_xml.find(cim + 'PetersenCoil.positionCurrent').text,
                'offset_current': petersen_coil_xml.find(cim + 'PetersenCoil.offsetCurrent').text,
                'nominal_u': petersen_coil_xml.find(cim + 'PetersenCoil.nominalU').text,
                'mode': petersen_coil_xml.find(cim + 'PetersenCoil.mode').get(rdf + 'resource')
            }

        
        for phase_tap_changer_asymmetrical_xml in root_EQ.iter(cim + 'PhaseTapChangerAsymmetrical'):
            phase_tap_changer_asymmetrical_id = phase_tap_changer_asymmetrical_xml.get(rdf + 'ID')
            phase_tap_changer_asymmetrical_dict[phase_tap_changer_asymmetrical_id] = {
                'ID': phase_tap_changer_asymmetrical_id,
                'name': phase_tap_changer_asymmetrical_xml.find(cim + 'IdentifiedObject.name').text,
                'neutral_u': phase_tap_changer_asymmetrical_xml.find(cim + 'TapChanger.neutralU').text,
                'low_step': phase_tap_changer_asymmetrical_xml.find(cim + 'TapChanger.lowStep').text,
                'high_step': phase_tap_changer_asymmetrical_xml.find(cim + 'TapChanger.highStep').text,
                'neutral_step': phase_tap_changer_asymmetrical_xml.find(cim + 'TapChanger.neutralStep').text,
                'normal_step': phase_tap_changer_asymmetrical_xml.find(cim + 'TapChanger.normalStep').text,
                'voltage_step_increment': phase_tap_changer_asymmetrical_xml.find(cim + 'PhaseTapChangerNonLinear.voltageStepIncrement').text,
                'x_min': phase_tap_changer_asymmetrical_xml.find(cim + 'PhaseTapChangerNonLinear.xMin').text,
                'x_max': phase_tap_changer_asymmetrical_xml.find(cim + 'PhaseTapChangerNonLinear.xMax').text,
                'winding_connection_angle': phase_tap_changer_asymmetrical_xml.find(cim + 'PhaseTapChangerAsymmetrical.windingConnectionAngle').text,
                'transformer_end': phase_tap_changer_asymmetrical_xml.find(cim + 'PhaseTapChanger.TransformerEnd').get(rdf + 'resource'),
                'tap_changer_control': phase_tap_changer_asymmetrical_xml.find(cim + 'TapChanger.TapChangerControl').get(rdf + 'resource')
            }

      
        for power_transformer_xml in root_EQ.iter(cim+'PowerTransformer'):
            power_transformer_id = power_transformer_xml.get(rdf+'ID')
            power_transformer_dict[power_transformer_id] = {
                'ID': power_transformer_id,
                'name': power_transformer_xml.find(cim+'IdentifiedObject.name').text,
                'equipment_container': power_transformer_xml.find(cim+'Equipment.EquipmentContainer').get(rdf+'resource')
            }

        #  # Loop through 'Power Transformer ends' elements and extract data
        for power_transformer_end_xml in root_EQ.iter(cim+'PowerTransformerEnd'):
            power_transformer_end_id = power_transformer_end_xml.get(rdf+'ID')
            power_transformer_end_dict[power_transformer_end_id] = {
                'ID': power_transformer_end_id,
                'name': power_transformer_end_xml.find(cim+'IdentifiedObject.name').text,
                'r': power_transformer_end_xml.find(cim+'PowerTransformerEnd.r').text,
                'x': power_transformer_end_xml.find(cim+'PowerTransformerEnd.x').text,
                'b': power_transformer_end_xml.find(cim+'PowerTransformerEnd.b').text,
                'g': power_transformer_end_xml.find(cim+'PowerTransformerEnd.g').text,
                'r0': power_transformer_end_xml.find(cim+'PowerTransformerEnd.r0').text,
                'x0': power_transformer_end_xml.find(cim+'PowerTransformerEnd.x0').text,
                'b0': power_transformer_end_xml.find(cim+'PowerTransformerEnd.b0').text,
                'g0': power_transformer_end_xml.find(cim+'PowerTransformerEnd.g0').text,
                'rground': power_transformer_end_xml.find(cim+'TransformerEnd.rground').text,
                'xground': power_transformer_end_xml.find(cim+'TransformerEnd.xground').text,
                'rated_s': power_transformer_end_xml.find(cim+'PowerTransformerEnd.ratedS').text,
                'rated_u': power_transformer_end_xml.find(cim+'PowerTransformerEnd.ratedU').text,
                'phase_angle_clock': power_transformer_end_xml.find(cim+'PowerTransformerEnd.phaseAngleClock').text,
                'connection_kind': power_transformer_end_xml.find(cim+'PowerTransformerEnd.connectionKind').get(rdf+'resource'),
                'base_voltage': power_transformer_end_xml.find(cim+'TransformerEnd.BaseVoltage').get(rdf+'resource'),
                'power_transformer': power_transformer_end_xml.find(cim+'PowerTransformerEnd.PowerTransformer').get(rdf+'resource'),
                'terminal': power_transformer_end_xml.find(cim+'TransformerEnd.Terminal').get(rdf+'resource')
            }

        
        for ratio_tap_changer_xml in root_EQ.iter(cim+'RatioTapChanger'):
            ratio_tap_changer_id = ratio_tap_changer_xml.get(rdf+'ID')
            ratio_tap_changer_dict[ratio_tap_changer_id] = {
                'ID': ratio_tap_changer_id,
                'name': ratio_tap_changer_xml.find(cim+'IdentifiedObject.name').text,
                'transformer_end': ratio_tap_changer_xml.find(cim+'RatioTapChanger.TransformerEnd').get(rdf+'resource'),
                'step': ""
            }
            
        for ratio_tap_changer_xml in root_SSH.iter(cim+'RatioTapChanger'):
            ratio_tap_changer_id = ratio_tap_changer_xml.get(rdf + 'about').replace("#", "")
            if ratio_tap_changer_id in ratio_tap_changer_dict:
                ratio_tap_changer_dict[ratio_tap_changer_id]['step'] = ratio_tap_changer_xml.find(cim+'TapChanger.step').text
                
        #print(ratio_tap_changer_dict)


        # Loop through 'RegulatingControl' elements and extract data
        for regulating_control_xml in root_EQ.iter(cim+'RegulatingControl'):
            regulating_control_id = regulating_control_xml.get(rdf+'ID')
            regulating_control_dict[regulating_control_id] = {
                'ID': regulating_control_id,
                'name': regulating_control_xml.find(cim+'IdentifiedObject.name').text,
                'mode': regulating_control_xml.find(cim+'RegulatingControl.mode').get(rdf+'resource'),
                'terminal': regulating_control_xml.find(cim+'RegulatingControl.Terminal').get(rdf+'resource'),
                'target_value': ""  # Initialize the target_value attribute
            }


        for regulating_control_xml in root_SSH.iter(cim+'RegulatingControl'):
            regulating_control_id = regulating_control_xml.get(rdf + 'about').replace("#", "")
            if regulating_control_id in  regulating_control_dict:
                regulating_control_dict[regulating_control_id]['target_value'] = regulating_control_xml.find(cim+'RegulatingControl.targetValue').text
            
            
        # Loop through 'Substation' elements and extract data
        for substation_xml in root_EQ.iter(cim+"Substation"):
            substation_id = substation_xml.get(rdf+"ID")
            substation_dict[substation_id] = {
                'ID': substation_id,
                'name': substation_xml.find(cim+"IdentifiedObject.name").text,
                'region': substation_xml.find(cim+"Substation.Region").get(rdf+"resource")
            }

        # Loop through 'SynchronousMachine' elements and extract data
        for synchronous_machine_xml in root_EQ.iter(cim+'SynchronousMachine'):
            synchronous_machine_id = synchronous_machine_xml.get(rdf+'ID')
            synchronous_machine_dict[synchronous_machine_id] = {
                'ID': synchronous_machine_id,
                'name': synchronous_machine_xml.find(cim+'IdentifiedObject.name').text,
                'equipment_container': synchronous_machine_xml.find(cim+'Equipment.EquipmentContainer').get(rdf+'resource'),
                'regulating_control': synchronous_machine_xml.find(cim+'RegulatingCondEq.RegulatingControl').get(rdf+'resource'),
                'generating_unit': synchronous_machine_xml.find(cim+'RotatingMachine.GeneratingUnit').get(rdf+'resource'),
                'active_power': "",
                'reactive_power': ""  # Initialize the active_power and reactive_power attributes
            }


        for synchronous_machine_xml in root_SSH.iter(cim+'SynchronousMachine'):
            synchronous_machine_id = synchronous_machine_xml.get(rdf + 'about').replace("#", "")
            if synchronous_machine_id in synchronous_machine_dict:
                synchronous_machine_dict[synchronous_machine_id]['active_power'] = synchronous_machine_xml.find(cim+'RotatingMachine.p').text
                synchronous_machine_dict[synchronous_machine_id]['reactive_power'] = synchronous_machine_xml.find(cim+'RotatingMachine.q').text
            

        # Loop through 'TapChangerControl' elements and extract data
        for tap_changer_control_xml in root_EQ.iter(cim+"TapChangerControl"):
            tap_changer_control_id = tap_changer_control_xml.get(rdf+"ID")
            tap_changer_control_dict[tap_changer_control_id] = {
                'ID': tap_changer_control_id,
                'name': tap_changer_control_xml.find(cim+'IdentifiedObject.name').text,
                'mode': tap_changer_control_xml.find(cim+"RegulatingControl.mode").text,
                'terminal': tap_changer_control_xml.find(cim+"RegulatingControl.Terminal").get(rdf+"resource")
            }
            


        # Loop through 'Terminal' elements and extract data
        for terminal_xml in root_EQ.iter(cim+'Terminal'):
            terminal_id = terminal_xml.get(rdf+'ID')
            terminal_dict[terminal_id] = {
                'ID': terminal_id,
                'name': terminal_xml.find(cim+'IdentifiedObject.name').text,
                'conducting_equipment': terminal_xml.find(cim+'Terminal.ConductingEquipment').get(rdf+'resource'),
                'connectivity_node': terminal_xml.find(cim+'Terminal.ConnectivityNode').get(rdf+'resource')
            }
        
        #print(terminal_dict)


        # Loop through 'VoltageLevel' elements and extract data
        for voltage_level_xml in root_EQ.iter(cim+'VoltageLevel'):
            voltage_level_id = voltage_level_xml.get(rdf+'ID')
            voltage_level_dict[voltage_level_id] = {
                'ID': voltage_level_id,
                'name': voltage_level_xml.find(cim+'IdentifiedObject.name').text,
                'substation': voltage_level_xml.find(cim+'VoltageLevel.Substation').get(rdf+'resource'),
                'base_voltage': voltage_level_xml.find(cim+'VoltageLevel.BaseVoltage').get(rdf+'resource')
            }
            
        
        def find_busbar(node_ID):
            for terminal_id, terminal_data in terminal_dict.items():
                if '#' + node_ID == terminal_data['connectivity_node']:
                    for busbar_id, busbar_data in busbar_section_dict.items():
                        if terminal_data['conducting_equipment'] == '#' + busbar_data['ID']:
                            return 'b'
            return 'n'        
        #print("Terminal ID:", terminal_id)
        connectivity_node = [[0 for i in range(3)] for j in range(len(connectivity_node_dict))]

        for i, (node_id, node_data) in enumerate(connectivity_node_dict.items()):
            connectivity_node[i][0] = node_data['name']
            
            
            voltage_level_name = voltage_level_dict[node_data['connectivity_node_container'].replace("#", "")]['name']
            connectivity_node[i][1] = float(voltage_level_name)
            
            connectivity_node[i][2] = find_busbar(node_id)

     
        terminal_keys_list = ['#' + key for key in terminal_dict.keys()]
        connectivity_node_keys_list = ['#' + key for key in connectivity_node_dict.keys()]
        
        #print(connectivity_node_keys_list)
        #print(len(connectivity_node_keys_list))
        
        terminal_dic = {}
        for i in range(len(terminal_keys_list)):
            terminal_dic[terminal_keys_list[i]] = i 
            
        connectivity_node_dic = {}
        for i in range(len(connectivity_node_keys_list)):
            connectivity_node_dic[connectivity_node_keys_list[i]] = i
        #print(connectivity_node_dic)

        
        #This part creates nested lists for each component filled with the required data for Panda Power 
        power_transformer = [[0 for i in range(8)] for j in range(len(power_transformer_dict))]

        for i, (pt_id, pt_data) in enumerate(power_transformer_dict.items()):
            power_transformer[i][0] = pt_data['name']
            power_transformer[i][7] = 'two_winding'
            t_i = []
            vl_i = []
            cn_i = []

            for pt_end_id, pt_end_data in power_transformer_end_dict.items():
                if '#'+ pt_data['ID'] == pt_end_data['power_transformer']:
                    t_i.append(terminal_keys_list.index(pt_end_data['terminal']))
                    cn_i.append(connectivity_node_keys_list.index(terminal_dict[terminal_keys_list[t_i[-1]].replace("#", "")]['connectivity_node']))
                    vl_i.append(connectivity_node[cn_i[-1]][1])


            min_vl_ind = vl_i.index(min(vl_i))
            max_vl_ind = vl_i.index(max(vl_i))

            power_transformer[i][1] = cn_i[min_vl_ind]
            power_transformer[i][4] = vl_i[min_vl_ind]
            power_transformer[i][3] = cn_i[max_vl_ind]
            power_transformer[i][6] = vl_i[max_vl_ind]

            if len(vl_i) == 3:
                power_transformer[i][2] = cn_i[3 - (min_vl_ind + max_vl_ind)]
                power_transformer[i][5] = vl_i[3 - (min_vl_ind + max_vl_ind)]
                power_transformer[i][7] = 'three_winding'

        # print(ac_line_segments_dict)
        # print(terminal_dict)
        AC_line_segment = [[0 for i in range(4)] for j in range(len(ac_line_segments_dict))]

        for i, (ac_line_segment_id,ac_line_segment_data) in enumerate(ac_line_segments_dict.items()):
            AC_line_segment[i][0] = ac_line_segment_data['name']
            AC_line_segment[i][3] = float(ac_line_segment_data['length'])
            
            count = 0
            for terminal_key in terminal_dict.keys():
                if '#' + ac_line_segment_data['ID'] == terminal_dict[terminal_key]['conducting_equipment']:
                    count += 1
                    if count == 1:
                        AC_line_segment[i][1] = connectivity_node_keys_list.index(terminal_dict[terminal_key]['connectivity_node'])
                    else:
                        AC_line_segment[i][2] = connectivity_node_keys_list.index(terminal_dict[terminal_key]['connectivity_node'])

        # print(AC_line_segment)

        breaker = [[0 for i in range(4)] for j in range(len(breaker_dict))]

        for i, (breaker_id,breaker_data) in enumerate(breaker_dict.items()):
            # breaker_data = breaker_dict[breaker_key]
            breaker[i][0] = breaker_data['name']
            if breaker_data['status'] == 'false':
                breaker[i][3] = True
            
            count = 0
            for terminal_key in terminal_dict.keys():
                if '#' + breaker_data['ID'] == terminal_dict[terminal_key]['conducting_equipment']:
                    count += 1
                    if count == 1:
                        breaker[i][1] = connectivity_node_keys_list.index(terminal_dict[terminal_key]['connectivity_node'])
                    else:
                        breaker[i][2] = connectivity_node_keys_list.index(terminal_dict[terminal_key]['connectivity_node'])
        # print(breaker)

        energy_consumer = [[0 for i in range(4)] for j in range(len(energy_consumer_dict))]

        for i, (energy_consumer_id, energy_consumer_data) in enumerate(energy_consumer_dict.items()):
            energy_consumer[i][0] = energy_consumer_data['name']
            energy_consumer[i][2] = float(energy_consumer_data['active_power'])
            energy_consumer[i][3] = float(energy_consumer_data['reactive_power'])

            for terminal_key in terminal_dict.keys():
                if '#' + energy_consumer_data['ID'] == terminal_dict[terminal_key]['conducting_equipment']:
                    energy_consumer[i][1] = connectivity_node_keys_list.index(terminal_dict[terminal_key]['connectivity_node'])
        # print(energy_consumer)
        generating_unit = [[0 for i in range(3)] for j in range(len(generating_unit_dict))]

        for i, (generating_unit_id, generating_unit_data) in enumerate(generating_unit_dict.items()):
            generating_unit[i][0] = generating_unit_data['name']
            generating_unit[i][2] = float(generating_unit_data['nominal_p'])
            
            for terminal_key in terminal_dict.keys():
                if '#' + generating_unit_data['ID'] == terminal_dict[terminal_key]['conducting_equipment']:
                    generating_unit[i][1] = connectivity_node_keys_list.index(terminal_dict[terminal_key]['connectivity_node'])
        #print(generating_unit)
        synchronous_machine = [[0 for i in range(3)] for j in range(len(synchronous_machine_dict))]

        for i, (synchronous_machine_id, synchronous_machine_data) in enumerate(synchronous_machine_dict.items()):
            synchronous_machine[i][0] = synchronous_machine_data['name']
            synchronous_machine[i][2] = float(synchronous_machine_data['active_power'])
            
            for terminal_key in terminal_dict.keys():
                if '#' + synchronous_machine_data['ID'] == terminal_dict[terminal_key]['conducting_equipment']:
                    synchronous_machine[i][1] = connectivity_node_keys_list.index(terminal_dict[terminal_key]['connectivity_node'])
        #print(synchronous_machine)

        linear_shunt_compensator = [[0 for i in range(4)] for j in range(len(linear_shunt_compensator_dict))]

        for i, (linear_shunt_compensator_id, linear_shunt_compensator_data) in enumerate(linear_shunt_compensator_dict.items()):
            linear_shunt_compensator[i][0] = linear_shunt_compensator_data['name']
            linear_shunt_compensator[i][2] = 0
            # reactive_power = float(voltage)**2 * float(susceptance)
            linear_shunt_compensator[i][3] = float(linear_shunt_compensator_data['nom_u'])**2 * float(linear_shunt_compensator_data['b_per_section'])
            
            
            for terminal_key in terminal_dict.keys():
                if '#' + linear_shunt_compensator_data['ID'] == terminal_dict[terminal_key]['conducting_equipment']:
                    linear_shunt_compensator[i][1] = connectivity_node_keys_list.index(terminal_dict[terminal_key]['connectivity_node'])
        # print(linear_shunt_compensator)

        #Panda power modelling

        net = pp.create_empty_network()

        #Busbars
        for i in range (len(connectivity_node_dict)):
            pp.create_bus (net, name=connectivity_node[i][0], vn_kv=connectivity_node[i][1], type = connectivity_node[i][2])
            
        #Transformers
        for i in range (len(power_transformer_dict)):
            if power_transformer[i][7] == 'two_winding':
                pp.create_transformer (net, power_transformer[i][3], power_transformer[i][1], name = power_transformer[i][0], std_type="25 MVA 110/20 kV")
            if power_transformer[i][7] == 'three_winding':
                pp.create.create_transformer3w (net, power_transformer[i][3], power_transformer[i][2], power_transformer[i][1], name = power_transformer[i][0], std_type="63/25/38 MVA 110/20/10 kV")
        #Lines
        for i in range (len(ac_line_segments_dict)):
            pp.create_line(net, AC_line_segment[i][1], AC_line_segment[i][2], length_km = AC_line_segment[i][3], std_type = "N2XS(FL)2Y 1x300 RM/35 64/110 kV",  name = AC_line_segment[i][0])

        #Breakers
        for i in range (len(breaker_dict)):
            pp.create_switch(net, breaker[i][1], breaker[i][2], et="b", type="CB", closed = breaker[i][3])

        #Load
        for i in range (len(energy_consumer_dict)):
            pp.create_load(net, energy_consumer[i][1], p_mw = energy_consumer[i][2], q_mvar = energy_consumer[i][3], name = energy_consumer[i][0])

        #Generator 
        for i in range (len(generating_unit_dict)):
            pp.create_sgen(net, generating_unit[i][1], p_mw = generating_unit[i][2], name = generating_unit[i][0])

        #for i in range (len(synchronous_machine_list)):
            #pp.create_sgen(net, synchronous_machine[i][1], p_mw = synchronous_machine[i][2], name = synchronous_machine[i][0])

        for i in range(len(linear_shunt_compensator_dict)):
            pp.create.create_shunt(net, linear_shunt_compensator[i][1], q_mvar=linear_shunt_compensator[i][3] , p_mw=0)#,  name=linear_shunt_compensator[i][0]) #vn_kv=None, step=1, max_step=1, name=None, in_service=True, index=None )   

        #pp.plotting.simple_plot(net)
        html_output(net, 'Model.html')
        pp.plotting.simple_plot(net, respect_switches=True, line_width=1.0, bus_size=1.0, ext_grid_size=1.0, trafo_size=1.0, plot_loads=True, plot_gens=True, 
                                plot_sgens=True, load_size=1.0, gen_size=1.0, sgen_size=1.0, switch_size=2.0, switch_distance=1.0, plot_line_switches=True, scale_size=True, bus_color='b', line_color='grey', 
                                dcline_color='c', trafo_color='k', ext_grid_color='y', switch_color='k', library='igraph', show_plot=True, ax=None)
        print(net)
        # After running the model and generating plots the output is stored in HTML format
        print("Model Run Successful")
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Model Run Successful: Open the Model.html File")
        msg.setWindowTitle("Model Run Status")
        msg.exec_()
        
        # Show a message box asking the user if they want to open the file
        #     msg = QMessageBox()
        #     msg.setIcon(QMessageBox.Information)
        #     msg.setText("Model Run Successful. Do you want to open the HTML file?")
        #     msg.setWindowTitle("Open File")
        #     msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        #     response = msg.exec_()
    
        #     if response == QMessageBox.Yes:
        #         self.open_html_file()
    
        # def open_html_file(self):
        #     # Get the current working directory
        #     cwd = os.getcwd()
        #     html_file_path = os.path.join(cwd, 'power_system_model_test_3.html')       

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())




