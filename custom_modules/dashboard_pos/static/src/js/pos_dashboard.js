/** @odoo-module **/
import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { _t } from "@web/core/l10n/translation";
import { Component } from "@odoo/owl";
import { onWillStart, onMounted, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { user } from "@web/core/user";
const actionRegistry = registry.category("actions");
export class PosDashboard extends Component {
  //Initializes the PosDashboard component,
  setup() {
    super.setup(...arguments);
    this.orm = useService('orm')
    this.user = user;
    this.actionService = useService("action");
    this.state = useState({
      payment_details: [],
      top_salesperson: [],
      sale_vs_cost: [],
      selling_product: [],
      total_sale: [],
      total_order_count: [],
      total_refund_count: [],
      new_customer_count: [],
      retained_customer_count: [],
      inactive_customer_count: [],
      top_selling_product_pos: [],
      top_selling_product_inv: [],
      low_selling_product_pos: [],
      low_selling_product_inv: [],
      total_session: [],
      today_refund_total: [],
      today_sale: [],
      today_sale_amount: [],
      from_date: this.get_today(),
      to_date: this.get_today(),
      daily_actual: [],
      daily_target: [],
      daily_percentage: [],
      weekly_actual: [],
      weekly_target: [],
      weekly_percentage: [],
      monthly_actual: [],
      monthly_target: [],
      monthly_percentage: [],
      history_data: [],
      // Accounting Reports State
      report_from_date: this.get_today(),
      report_to_date: this.get_today(),
      current_report_type: 'profit_loss',
      report_loading: false,
      profit_loss_data: [],
      balance_sheet_assets: [],
      balance_sheet_liabilities: [],
      trial_balance_data: [],
      current_report_data: [],
      // POS Order Report State
      pos_from_date: this.get_today(),
      pos_to_date: this.get_today(),
      pos_report_loading: false,
      pos_total_orders: 0,
      pos_total_amount: '0.00',
      pos_avg_order: '0.00',
      pos_top_products: [],
      // Pricing Scenarios State
      pricing_scenarios_loading: false,
      pricing_scenarios_data: null,
      pricing_scenarios_start_date: null,
      pricing_scenarios_end_date: null,
      pricing_scenarios_current_tab: 'break_even',
      pricing_scenarios_weighting_mode: 'uniform', // 'uniform' or 'weighted'
      pricing_scenarios_custom_target: 25000,
      pricing_scenarios_error: null,
    });
    // When the component is about to start, fetch data in tiles
    onWillStart(async () => {
      await this.fetch_data();
    });
    //When the component is mounted, render various charts
    onMounted(async () => {
      // Add loading states
      this.addLoadingStates();

      // Render charts with animations
      await this.render_top_customer_graph();
      await this.render_top_product_graph();
      await this.render_product_category_graph();
      await this.onclick_pos_sales('Weekly');

      // Generate default reports
      await this.generatePosReport();
      await this.generateAccountingReport();

      // Initialize pricing scenarios date range
      this.initializePricingScenariosDateRange();

      // Add entrance animations
      this.addEntranceAnimations();
    });
  }
  get_today() {
    return new Date().toISOString().split('T')[0];
  }
  async fetch_data() {
    //  Function to fetch all the pos details
    var result = await this.orm.call('pos.order', 'get_refund_details', [])
    this.state.total_sale = result['total_sale'],
      this.state.total_order_count = result['total_order_count']
    this.state.total_refund_count = result['total_refund_count']
    this.state.new_customer_count = result['new_customer_count']
    this.state.retained_customer_count = result['retained_customer_count']
    this.state.inactive_customer_count = result['inactive_customer_count']
    this.state.top_selling_product_pos = result['top_selling_product_pos']
    this.state.top_selling_product_inv = result['top_selling_product_inv']
    this.state.low_selling_product_pos = result['low_selling_product_pos']
    this.state.low_selling_product_inv = result['low_selling_product_inv']
    this.state.total_session = result['total_session']
    this.state.today_refund_total = result['today_refund_total']
    this.state.today_sale = result['today_sale']
    this.state.today_sale_amount = result['today_sale_amount']
    this.state.payment_details = result['payment_details']
    this.state.history_data = result['history_data']
    var data = await this.orm.call('pos.order', 'get_details', [])
    this.state.top_salesperson = data['salesperson']
    this.state.selling_product = data['selling_product']
  }
  async onDateChange(ev) {
    const { id, value } = ev.target;
    if (id === "from_date_cus") {
      this.state.from_date = value;
    } else if (id === "to_date_cus") {
      this.state.to_date = value;
    }

    // When both dates are selected, fetch and update dashboard
    const from_date_cus = this.state.from_date;
    const to_date_cus = this.state.to_date;

    if (from_date_cus && to_date_cus) {
      const res = await this.orm.call(
        "pos.order",
        "get_all_data",
        [from_date_cus, to_date_cus]
      );
      // Update your Owl state fields with the result
      this.state.top_selling_product_pos = res["top_selling_product_pos"];
      this.state.top_selling_product_inv = res["top_selling_product_inv"];
      this.state.low_selling_product_pos = res["low_selling_product_pos"];
      this.state.low_selling_product_inv = res["low_selling_product_inv"];
      this.state.payment_details = res["payment_details"];
      // Optionally call your dashboard/chart render here
    } else {
      console.log("Please select both dates.");
    }
  }
  async onSubmitTarget(ev) {
    ev.preventDefault();
    var monthly_target_input = $("#float_input").val();
    console.log('monthly_target_inputmonthly_target_input', monthly_target_input)
    var self = this;
    const get_target_values = await this.orm.call(
      "pos.order",
      "get_target",
      [monthly_target_input]
    );
    console.log('llllllllllllll', get_target_values)
    this.state.daily_actual = get_target_values['daily_actual'];
    this.state.daily_target = get_target_values['daily_target'];
    this.state.daily_percentage = get_target_values['daily_percentage'];
    this.state.weekly_actual = get_target_values['weekly_actual'];
    this.state.weekly_target = get_target_values['weekly_target'];
    this.state.weekly_percentage = get_target_values['weekly_percentage'];
    this.state.monthly_actual = get_target_values['monthly_actual'];
    this.state.monthly_target = get_target_values['monthly_target'];
    this.state.monthly_percentage = get_target_values['monthly_percentage'];



  }
  pos_order_today(e) {
    //To get the details of today's order
    var self = this;
    var date = new Date();
    var yesterday = new Date(date.getTime());
    yesterday.setDate(date.getDate());
    yesterday.setHours(0, 0, 0, 0);
    e.stopPropagation();
    e.preventDefault();
    this.user.hasGroup('hr.group_hr_user').then(function (has_group) {
      if (has_group) {
        var options = {
          on_reverse_breadcrumb: self.on_reverse_breadcrumb,
        };
        self.actionService.doAction({
          name: _t("Today Order"),
          type: 'ir.actions.act_window',
          res_model: 'pos.order',
          view_mode: 'tree,form,calendar',
          view_type: 'form',
          views: [[false, 'list'], [false, 'form']],
          domain: [['date_order', '<=', date], ['date_order', '>=', yesterday], ['state', 'in', ['paid', 'done', 'invoiced']]],
          target: 'current'
        }, options)
      }
    });
  }
  pos_refund_orders(e) {
    //   To get the details of refund orders
    var self = this;
    var date = new Date();
    var yesterday = new Date(date.getTime());
    yesterday.setDate(date.getDate() - 1);
    e.stopPropagation();
    e.preventDefault();
    this.user.hasGroup('hr.group_hr_user').then(function (has_group) {
      if (has_group) {
        var options = {
          on_reverse_breadcrumb: self.on_reverse_breadcrumb,
        };
        self.actionService.doAction({
          name: _t("Refund Orders"),
          type: 'ir.actions.act_window',
          res_model: 'pos.order',
          view_mode: 'tree,form,calendar',
          view_type: 'form',
          views: [[false, 'list'], [false, 'form']],
          domain: [['amount_total', '<', 0.0]],
          target: 'current'
        }, options)
      }
    });
  }
  pos_refund_today_orders(e) {
    //  To get the details of today's order
    var self = this;
    var date = new Date();
    var yesterday = new Date(date.getTime());
    yesterday.setDate(date.getDate() - 1);
    e.stopPropagation();
    e.preventDefault();
    this.user.hasGroup('hr.group_hr_user').then(function (has_group) {
      if (has_group) {
        var options = {
          on_reverse_breadcrumb: self.on_reverse_breadcrumb,
        };
        self.actionService.doAction({
          name: _t("Refund Orders"),
          type: 'ir.actions.act_window',
          res_model: 'pos.order',
          view_mode: 'tree,form,calendar',
          view_type: 'form',
          views: [[false, 'list'], [false, 'form']],
          domain: [['amount_total', '<', 0.0], ['date_order', '<=', date], ['date_order', '>=', yesterday]],
          target: 'current'
        }, options)
      }
    });
  }
  pos_order(e) {
    //    To get total orders details
    var self = this;
    var date = new Date();
    var yesterday = new Date(date.getTime());
    yesterday.setDate(date.getDate() - 1);
    e.stopPropagation();
    e.preventDefault();
    this.user.hasGroup('hr.group_hr_user').then(function (has_group) {
      if (has_group) {
        var options = {
          on_reverse_breadcrumb: self.on_reverse_breadcrumb,
        };
        self.actionService.doAction({
          name: _t("Total Order"),
          type: 'ir.actions.act_window',
          res_model: 'pos.order',
          view_mode: 'tree,form,calendar',
          view_type: 'form',
          views: [[false, 'list'], [false, 'form']],
          domain: [['state', 'in', ['paid', 'done', 'invoiced']]],
          target: 'current'
        }, options)
      }
    });
  }
  new_customers(e) {
    var self = this;
    var date = new Date();
    var yesterday = new Date(date.getTime());
    yesterday.setDate(date.getDate() - 1);
    e.stopPropagation();
    e.preventDefault();

    this.user.hasGroup('hr.group_hr_user').then(function (has_group) {
      if (has_group) {
        var options = {
          on_reverse_breadcrumb: self.on_reverse_breadcrumb,
        };
        self.actionService.doAction({
          name: _t("New Customers"),
          type: 'ir.actions.act_window',
          res_model: 'res.partner',
          view_mode: 'tree,form,calendar',
          view_type: 'form',
          views: [[false, 'list'], [false, 'form']],
          domain: [['is_new_customer', '=', 1]],

          //                    domain: [['date_order', '=', date]],
          target: 'current'
        }, options)
      }
    });

  }

  retained_customers(e) {
    var self = this;
    var date = new Date();
    var yesterday = new Date(date.getTime());
    yesterday.setDate(date.getDate() - 1);
    e.stopPropagation();
    e.preventDefault();

    this.user.hasGroup('hr.group_hr_user').then(function (has_group) {
      if (has_group) {
        var options = {
          on_reverse_breadcrumb: self.on_reverse_breadcrumb,
        };
        self.actionService.doAction({
          name: _t("Retained Customers"),
          type: 'ir.actions.act_window',
          res_model: 'res.partner',
          view_mode: 'tree,form,calendar',
          view_type: 'form',
          views: [[false, 'list'], [false, 'form']],
          domain: [['is_new_customer', '>', 1]],

          //                    domain: [['date_order', '=', date]],
          target: 'current'
        }, options)
      }
    });

  }
  inactive_customers(e) {
    var self = this;
    var date = new Date();
    var yesterday = new Date(date.getTime());
    yesterday.setDate(date.getDate() - 1);
    e.stopPropagation();
    e.preventDefault();

    this.user.hasGroup('hr.group_hr_user').then(function (has_group) {
      if (has_group) {
        var options = {
          on_reverse_breadcrumb: self.on_reverse_breadcrumb,
        };
        self.actionService.doAction({
          name: _t("Inactive Customers"),
          type: 'ir.actions.act_window',
          res_model: 'res.partner',
          view_mode: 'tree,form,calendar',
          view_type: 'form',
          views: [[false, 'list'], [false, 'form']],
          domain: [['inactive_customer', '=', true]],
          target: 'current'
        }, options)
      }
    });

  }

  pos_session(e) {
    //    To get the Session wise details
    var self = this;
    e.stopPropagation();
    e.preventDefault();
    this.user.hasGroup('hr.group_hr_user').then(function (has_group) {
      if (has_group) {
        var options = {
          on_reverse_breadcrumb: self.on_reverse_breadcrumb,
        };
        self.actionService.doAction({
          name: _t("sessions"),
          type: 'ir.actions.act_window',
          res_model: 'pos.session',
          view_mode: 'tree,form,calendar',
          view_type: 'form',
          views: [[false, 'list'], [false, 'form']],
          target: 'current'
        }, options)
      }
    });
  }
  async onclick_pos_sales_cost(ev) {
    const option_pos_sales_cost = ev.target.value;
    const sale_vs_cost = await this.orm.call('pos.order', 'get_sale_vs_cost', [option_pos_sales_cost]);
    this.state.sale_vs_cost = sale_vs_cost || [0, 0, 0];
  }


  onclick_pos_sales(events) {
    //  Modern Sale bar chart with advanced styling
    var option = $(events.target).val();
    var self = this
    var canvas = document.getElementById("canvas_1");
    if (!canvas) {
      console.error("Canvas element not found");
      return;
    }
    var ctx = canvas.getContext("2d");
    this.orm.call('pos.order', 'get_department', [option])
      .then(function (arrays) {
        var data = {
          labels: arrays[1],
          datasets: [
            {
              label: arrays[2],
              data: arrays[0],
              backgroundColor: [
                "rgba(102, 126, 234, 0.8)",
                "rgba(240, 147, 251, 0.8)",
                "rgba(79, 172, 254, 0.8)",
                "rgba(67, 233, 123, 0.8)",
                "rgba(250, 112, 154, 0.8)",
                "rgba(168, 237, 234, 0.8)"
              ],
              borderColor: [
                "rgba(102, 126, 234, 1)",
                "rgba(240, 147, 251, 1)",
                "rgba(79, 172, 254, 1)",
                "rgba(67, 233, 123, 1)",
                "rgba(250, 112, 154, 1)",
                "rgba(168, 237, 234, 1)"
              ],
              borderWidth: 2,
              borderRadius: 8,
              borderSkipped: false,
            },
          ]
        };

        // Modern chart options
        var options = {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: true,
              position: "top",
              labels: {
                usePointStyle: true,
                padding: 20,
                font: {
                  size: 12,
                  weight: '500'
                },
                color: '#2c3e50'
              }
            },
            tooltip: {
              backgroundColor: 'rgba(0, 0, 0, 0.8)',
              titleColor: 'white',
              bodyColor: 'white',
              borderColor: 'rgba(102, 126, 234, 1)',
              borderWidth: 1,
              cornerRadius: 8,
              displayColors: true,
              callbacks: {
                label: function (context) {
                  return context.dataset.label + ': ' + context.parsed.y.toLocaleString();
                }
              }
            }
          },
          scales: {
            x: {
              grid: {
                display: false
              },
              ticks: {
                color: '#7f8c8d',
                font: {
                  size: 11,
                  weight: '500'
                }
              }
            },
            y: {
              beginAtZero: true,
              grid: {
                color: 'rgba(0, 0, 0, 0.05)',
                drawBorder: false
              },
              ticks: {
                color: '#7f8c8d',
                font: {
                  size: 11,
                  weight: '500'
                },
                callback: function (value) {
                  return value.toLocaleString();
                }
              }
            }
          },
          animation: {
            duration: 2000,
            easing: 'easeInOutQuart'
          },
          interaction: {
            intersect: false,
            mode: 'index'
          }
        };

        // Destroy existing chart
        if (window.myCharts != undefined) {
          window.myCharts.destroy();
        }

        // Create new chart with modern styling
        window.myCharts = new Chart(ctx, {
          type: "bar",
          data: data,
          options: options
        });

      });
  }
  render_top_customer_graph() {
    //      To render the top customer pie chart
    var self = this
    const canvas = document.querySelector('.top_customer');
    if (!canvas) {
      console.warn('top_customer canvas not found; skipping chart render');
      return;
    }
    const ctx = canvas.getContext('2d');
    this.orm.call('pos.order', 'get_the_top_customer')
      .then(function (arrays) {
        var data = {
          labels: arrays[1],
          datasets: [
            {
              label: "",
              data: arrays[0],
              backgroundColor: [
                "rgb(148, 22, 227)",
                "rgba(54, 162, 235)",
                "rgba(75, 192, 192)",
                "rgba(153, 102, 255)",
                "rgba(10,20,30)"
              ],
              borderColor: [
                "rgba(255, 99, 132,)",
                "rgba(54, 162, 235,)",
                "rgba(75, 192, 192,)",
                "rgba(153, 102, 255,)",
                "rgba(10,20,30,)"
              ],
              borderWidth: 1
            },

          ]
        };
        //options
        var options = {
          responsive: true,
          scales: {
            x: {
              title: {
                display: true,
                text: "Top Customer",
                position: "top",
                fontSize: 24,
                color: "#111"
              }
            }
          },
          legend: {
            display: true,
            position: "bottom",
            labels: {
              fontColor: "#333",
              fontSize: 16
            }
          }
        };
        //create Chart class object
        var chart = new Chart(ctx, {
          type: "pie",
          data: data,
          options: options
        });

      });
  }
  render_top_product_graph() {
    //   To render the top product graph
    var self = this
    const canvas = document.querySelector('.top_selling_product');
    if (!canvas) {
      console.warn('top_selling_product canvas not found; skipping chart render');
      return;
    }
    const ctx = canvas.getContext('2d');
    this.orm.call('pos.order', 'get_the_top_products')
      .then(function (arrays) {
        var data = {

          labels: arrays[1],
          datasets: [
            {
              label: "Quantity",
              data: arrays[0],
              backgroundColor: [
                "rgba(255, 99, 132,1)",
                "rgba(54, 162, 235,1)",
                "rgba(75, 192, 192,1)",
                "rgba(153, 102, 255,1)",
                "rgba(10,20,30,1)"
              ],
              borderColor: [
                "rgba(255, 99, 132, 0.2)",
                "rgba(54, 162, 235, 0.2)",
                "rgba(75, 192, 192, 0.2)",
                "rgba(153, 102, 255, 0.2)",
                "rgba(10,20,30,0.3)"
              ],
              borderWidth: 1
            },

          ]
        };
        //options
        var options = {
          responsive: true,
          indexAxis: 'y',
          legend: {
            display: true,
            position: "bottom",
            labels: {
              fontColor: "#333",
              fontSize: 16
            }
          },
          scales: {
            x: {
              title: {
                display: true,
                text: "Top products",
                position: "top",
                fontSize: 24,
                color: "#111"
              }
            }
          },
        };
        //create Chart class object
        var chart = new Chart(ctx, {
          type: "bar",
          data: data,
          options: options
        });
      });
  }
  render_product_category_graph() {
    //    To render the product category graph
    var self = this
    var ctx = $(".top_product_categories");
    this.orm.call('pos.order', 'get_the_top_categories')
      .then(function (arrays) {
        var data = {
          labels: arrays[1],
          datasets: [
            {
              label: "Quantity",
              data: arrays[0],
              backgroundColor: [
                "rgba(255, 99, 132,1)",
                "rgba(54, 162, 235,1)",
                "rgba(75, 192, 192,1)",
                "rgba(153, 102, 255,1)",
                "rgba(10,20,30,1)"
              ],
              borderColor: [
                "rgba(255, 99, 132, 0.2)",
                "rgba(54, 162, 235, 0.2)",
                "rgba(75, 192, 192, 0.2)",
                "rgba(153, 102, 255, 0.2)",
                "rgba(10,20,30,0.3)"
              ],
              borderWidth: 1
            },
          ]
        };
        //options
        var options = {
          responsive: true,
          scales: {
            x: {
              title: {
                display: true,
                text: "Top product categories",
                position: "top",
                fontSize: 24,
                color: "#111"
              }
            }
          },
          legend: {
            display: true,
            position: "bottom",
            labels: {
              fontColor: "#333",
              fontSize: 16
            }
          },
          indexAxis: 'y',
        };
        //create Chart class object
        var chart = new Chart(ctx, {
          type: "bar",
          data: data,
          options: options
        });
      });
  }

  // Modern animation and loading methods
  addLoadingStates() {
    // Add loading class to KPI cards
    const kpiCards = document.querySelectorAll('.modern-kpi-card');
    kpiCards.forEach(card => {
      card.classList.add('loading');
    });

    // Remove loading after a short delay
    setTimeout(() => {
      kpiCards.forEach(card => {
        card.classList.remove('loading');
      });
    }, 1000);
  }

  addEntranceAnimations() {
    // Animate KPI cards with staggered delay
    const kpiCards = document.querySelectorAll('.modern-kpi-card');
    kpiCards.forEach((card, index) => {
      card.style.animationDelay = `${index * 0.1}s`;
      card.classList.add('fade-in');
    });

    // Animate chart cards
    const chartCards = document.querySelectorAll('.modern-chart-card');
    chartCards.forEach((card, index) => {
      card.style.animationDelay = `${(index + 1) * 0.2}s`;
      card.classList.add('slide-in-left');
    });

    // Animate table cards
    const tableCards = document.querySelectorAll('.modern-table-card');
    tableCards.forEach((card, index) => {
      card.style.animationDelay = `${(index + 2) * 0.15}s`;
      card.classList.add('slide-in-right');
    });
  }

  // Enhanced number formatting
  formatNumber(value) {
    if (typeof value === 'number') {
      return value.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      });
    }
    return value;
  }

  // Add hover effects to KPI cards
  addKpiHoverEffects() {
    const kpiCards = document.querySelectorAll('.modern-kpi-card');
    kpiCards.forEach(card => {
      card.addEventListener('mouseenter', function () {
        this.style.transform = 'translateY(-8px) scale(1.02)';
      });

      card.addEventListener('mouseleave', function () {
        this.style.transform = 'translateY(0) scale(1)';
      });
    });
  }

  // Modern tooltip for KPI values
  addKpiTooltips() {
    const kpiValues = document.querySelectorAll('.kpi-value');
    kpiValues.forEach(value => {
      value.title = `Current Value: ${value.textContent}`;
    });
  }

  // ===== ACCOUNTING REPORTS METHODS =====

  // Handle report date change
  async onReportDateChange() {
    const fromDate = document.getElementById('report_from_date').value;
    const toDate = document.getElementById('report_to_date').value;

    if (fromDate && toDate) {
      this.state.report_from_date = fromDate;
      this.state.report_to_date = toDate;
      await this.generateAccountingReport();
    }
  }

  // Handle report type change
  async onReportTypeChange() {
    const reportType = document.getElementById('report_type').value;
    this.state.current_report_type = reportType;
    await this.generateAccountingReport();
  }

  // Generate accounting report based on current settings
  async generateAccountingReport() {
    this.state.report_loading = true;

    try {
      switch (this.state.current_report_type) {
        case 'profit_loss':
          await this.fetchProfitLossReport();
          break;
        case 'balance_sheet':
          await this.fetchBalanceSheetReport();
          break;
        case 'trial_balance':
          await this.fetchTrialBalanceReport();
          break;
      }
    } catch (error) {
      console.error('Error generating accounting report:', error);
    } finally {
      this.state.report_loading = false;
    }
  }

  // Fetch Profit & Loss Report
  async fetchProfitLossReport() {
    try {
      console.log('Fetching Profit & Loss report...');
      // Get accounts of income and expense types
      const accountDomain = [
        ['account_type', 'in', ['income', 'income_other', 'expense', 'expense_depreciation', 'expense_direct_cost']]
      ];

      const accounts = await this.orm.searchRead('account.account', accountDomain, [
        'id', 'name', 'code', 'account_type'
      ]);

      console.log('Found accounts:', accounts.length);

      // Get move lines for these accounts in the date range
      const moveLineDomain = [
        ['date', '>=', this.state.report_from_date],
        ['date', '<=', this.state.report_to_date],
        ['move_id.state', '=', 'posted'],
        ['account_id', 'in', accounts.map(acc => acc.id)]
      ];

      const moveLines = await this.orm.searchRead('account.move.line', moveLineDomain, [
        'account_id', 'debit', 'credit'
      ]);

      // Group by account and calculate totals
      const accountTotals = {};
      accounts.forEach(account => {
        accountTotals[account.id] = {
          id: account.id,
          name: account.name,
          code: account.code,
          debit: 0,
          credit: 0,
          balance: 0
        };
      });

      moveLines.forEach(line => {
        const accountId = line.account_id[0];
        if (accountTotals[accountId]) {
          accountTotals[accountId].debit += line.debit || 0;
          accountTotals[accountId].credit += line.credit || 0;
        }
      });

      // Calculate balance (credit - debit for income, debit - credit for expense)
      Object.values(accountTotals).forEach(account => {
        if (account.name.toLowerCase().includes('income') ||
          account.name.toLowerCase().includes('revenue') ||
          account.name.toLowerCase().includes('sales')) {
          account.balance = account.credit - account.debit;
        } else {
          account.balance = account.debit - account.credit;
        }
      });

      // Convert to array and format
      this.state.profit_loss_data = Object.values(accountTotals).map(account => ({
        id: account.id,
        name: `${account.code} - ${account.name}`,
        debit: this.formatCurrency(account.debit),
        credit: this.formatCurrency(account.credit),
        balance: this.formatCurrency(account.balance),
        level: 1,
        type: 'income_expense'
      }));

      console.log('Profit & Loss data:', this.state.profit_loss_data);
      this.state.current_report_data = this.state.profit_loss_data;

    } catch (error) {
      console.error('Error fetching Profit & Loss report:', error);
      this.state.profit_loss_data = [];
    }
  }

  // Fetch Balance Sheet Report
  async fetchBalanceSheetReport() {
    try {
      // Get accounts of asset, liability, and equity types
      const accountDomain = [
        ['account_type', 'in', ['asset_receivable', 'asset_cash', 'asset_current', 'asset_non_current', 'asset_prepayments', 'asset_fixed', 'liability_payable', 'liability_credit_card', 'liability_current', 'liability_non_current', 'equity', 'equity_unaffected']]
      ];

      const accounts = await this.orm.searchRead('account.account', accountDomain, [
        'id', 'name', 'code', 'account_type'
      ]);

      // Get move lines for these accounts up to the end date
      const moveLineDomain = [
        ['date', '<=', this.state.report_to_date],
        ['move_id.state', '=', 'posted'],
        ['account_id', 'in', accounts.map(acc => acc.id)]
      ];

      const moveLines = await this.orm.searchRead('account.move.line', moveLineDomain, [
        'account_id', 'debit', 'credit'
      ]);

      // Group by account and calculate totals
      const accountTotals = {};
      accounts.forEach(account => {
        accountTotals[account.id] = {
          id: account.id,
          name: account.name,
          code: account.code,
          account_type: account.account_type,
          debit: 0,
          credit: 0,
          balance: 0
        };
      });

      moveLines.forEach(line => {
        const accountId = line.account_id[0];
        if (accountTotals[accountId]) {
          accountTotals[accountId].debit += line.debit || 0;
          accountTotals[accountId].credit += line.credit || 0;
        }
      });

      // Calculate balance based on account type
      Object.values(accountTotals).forEach(account => {
        if (account.account_type.startsWith('asset')) {
          // Assets: debit - credit
          account.balance = account.debit - account.credit;
        } else if (account.account_type.startsWith('liability') || account.account_type.startsWith('equity')) {
          // Liabilities and Equity: credit - debit
          account.balance = account.credit - account.debit;
        }
      });

      // Convert to array and format
      const allData = Object.values(accountTotals).map(account => ({
        id: account.id,
        name: `${account.code} - ${account.name}`,
        debit: this.formatCurrency(account.debit),
        credit: this.formatCurrency(account.credit),
        balance: this.formatCurrency(account.balance),
        level: 1,
        type: account.account_type.startsWith('asset') ? 'asset' : 'liability'
      }));

      this.state.balance_sheet_assets = allData.filter(item => item.type === 'asset');
      this.state.balance_sheet_liabilities = allData.filter(item => item.type === 'liability');
      this.state.current_report_data = allData;

    } catch (error) {
      console.error('Error fetching Balance Sheet report:', error);
      this.state.balance_sheet_assets = [];
      this.state.balance_sheet_liabilities = [];
    }
  }

  // Fetch Trial Balance Report
  async fetchTrialBalanceReport() {
    try {
      // Get all accounts
      const accounts = await this.orm.searchRead('account.account', [], [
        'id', 'name', 'code', 'account_type'
      ]);

      // Get move lines for these accounts in the date range
      const moveLineDomain = [
        ['date', '>=', this.state.report_from_date],
        ['date', '<=', this.state.report_to_date],
        ['move_id.state', '=', 'posted'],
        ['account_id', 'in', accounts.map(acc => acc.id)]
      ];

      const moveLines = await this.orm.searchRead('account.move.line', moveLineDomain, [
        'account_id', 'debit', 'credit'
      ]);

      // Group by account and calculate totals
      const accountTotals = {};
      accounts.forEach(account => {
        accountTotals[account.id] = {
          id: account.id,
          name: account.name,
          code: account.code,
          account_type: account.account_type,
          debit: 0,
          credit: 0,
          balance: 0
        };
      });

      moveLines.forEach(line => {
        const accountId = line.account_id[0];
        if (accountTotals[accountId]) {
          accountTotals[accountId].debit += line.debit || 0;
          accountTotals[accountId].credit += line.credit || 0;
        }
      });

      // Calculate balance based on account type
      Object.values(accountTotals).forEach(account => {
        if (account.account_type.startsWith('asset')) {
          // Assets: debit - credit
          account.balance = account.debit - account.credit;
        } else if (account.account_type.startsWith('liability') || account.account_type.startsWith('equity')) {
          // Liabilities and Equity: credit - debit
          account.balance = account.credit - account.debit;
        } else {
          // Income and Expense: credit - debit
          account.balance = account.credit - account.debit;
        }
      });

      // Convert to array and format
      this.state.trial_balance_data = Object.values(accountTotals).map(account => ({
        id: account.id,
        name: `${account.code} - ${account.name}`,
        debit: this.formatCurrency(account.debit),
        credit: this.formatCurrency(account.credit),
        balance: this.formatCurrency(account.balance),
        level: 1,
        type: this.determineAccountType(account.name)
      }));

      this.state.current_report_data = this.state.trial_balance_data;

    } catch (error) {
      console.error('Error fetching Trial Balance report:', error);
      this.state.trial_balance_data = [];
    }
  }

  // Parse report lines data from financial.report
  parseReportLines(reportLines) {
    const reportData = [];

    if (!reportLines || !Array.isArray(reportLines)) {
      return reportData;
    }

    reportLines.forEach((line, index) => {
      if (line && line.name) {
        const name = line.name || '';
        const debit = this.parseAmount(line.debit || 0);
        const credit = this.parseAmount(line.credit || 0);
        const balance = this.parseAmount(line.balance || 0);

        // Determine level from the line data
        const level = line.level || 1;

        // Determine account type for balance sheet
        const type = this.determineAccountType(name);

        reportData.push({
          id: line.id || index,
          name: name,
          debit: debit,
          credit: credit,
          balance: balance,
          level: level,
          type: type
        });
      }
    });

    return reportData;
  }

  // Parse amount string to number
  parseAmount(amountStr) {
    if (!amountStr) return 0;

    // Remove currency symbols and commas
    const cleanStr = amountStr.replace(/[$,]/g, '').trim();

    // Handle parentheses for negative amounts
    if (cleanStr.includes('(') && cleanStr.includes(')')) {
      return -parseFloat(cleanStr.replace(/[()]/g, '')) || 0;
    }

    return parseFloat(cleanStr) || 0;
  }

  // Determine account level based on indentation
  determineAccountLevel(cell) {
    if (!cell) return 0;

    const style = cell.getAttribute('style') || '';
    const paddingMatch = style.match(/padding-left:\s*(\d+)px/);

    if (paddingMatch) {
      const padding = parseInt(paddingMatch[1]);
      if (padding >= 40) return 2; // Sub-account
      if (padding >= 20) return 1; // Main account
    }

    // Check for bold text (usually indicates main accounts)
    const isBold = cell.querySelector('b, strong') ||
      cell.style.fontWeight === 'bold' ||
      cell.classList.contains('font-weight-bold');

    return isBold ? 1 : 0;
  }

  // Determine account type for balance sheet
  determineAccountType(accountName) {
    const name = accountName.toLowerCase();

    if (name.includes('asset') || name.includes('cash') || name.includes('bank') ||
      name.includes('inventory') || name.includes('receivable')) {
      return 'asset';
    }

    if (name.includes('liability') || name.includes('payable') || name.includes('debt')) {
      return 'liability';
    }

    if (name.includes('equity') || name.includes('capital') || name.includes('retained')) {
      return 'equity';
    }

    return 'other';
  }

  // Format currency for display
  formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(amount);
  }

  // ===== POS ORDER REPORT METHODS =====

  // Handle POS date change
  async onPosDateChange() {
    const fromDate = document.getElementById('pos_from_date').value;
    const toDate = document.getElementById('pos_to_date').value;

    if (fromDate && toDate) {
      this.state.pos_from_date = fromDate;
      this.state.pos_to_date = toDate;
    }
  }

  // Generate POS Order Report
  async generatePosReport() {
    this.state.pos_report_loading = true;

    try {
      await this.fetchPosOrderData();
      await this.fetchTopSellingProducts();
    } catch (error) {
      console.error('Error generating POS report:', error);
    } finally {
      this.state.pos_report_loading = false;
    }
  }

  // Fetch POS Order Data
  async fetchPosOrderData() {
    try {
      // Get POS orders for the date range
      const domain = [
        ['date_order', '>=', this.state.pos_from_date],
        ['date_order', '<=', this.state.pos_to_date + ' 23:59:59'],
        ['state', 'in', ['paid', 'done', 'invoiced']]
      ];

      const orders = await this.orm.searchRead('pos.order', domain, [
        'id', 'amount_total', 'date_order'
      ]);

      // Calculate totals
      const totalOrders = orders.length;
      const totalAmount = orders.reduce((sum, order) => sum + (order.amount_total || 0), 0);
      const avgOrder = totalOrders > 0 ? totalAmount / totalOrders : 0;

      // Update state
      this.state.pos_total_orders = totalOrders;
      this.state.pos_total_amount = this.formatCurrency(totalAmount);
      this.state.pos_avg_order = this.formatCurrency(avgOrder);

    } catch (error) {
      console.error('Error fetching POS order data:', error);
      this.state.pos_total_orders = 0;
      this.state.pos_total_amount = '0.00';
      this.state.pos_avg_order = '0.00';
    }
  }

  // Fetch Top Selling Products
  async fetchTopSellingProducts() {
    try {
      // Get POS order lines for the date range
      const domain = [
        ['order_id.date_order', '>=', this.state.pos_from_date],
        ['order_id.date_order', '<=', this.state.pos_to_date + ' 23:59:59'],
        ['order_id.state', 'in', ['paid', 'done', 'invoiced']]
      ];

      const orderLines = await this.orm.searchRead('pos.order.line', domain, [
        'product_id', 'qty', 'price_subtotal'
      ]);

      // Group by product and calculate totals
      const productTotals = {};
      orderLines.forEach(line => {
        const productId = line.product_id[0];
        const productName = line.product_id[1];

        if (!productTotals[productId]) {
          productTotals[productId] = {
            id: productId,
            name: productName,
            quantity: 0,
            amount: 0
          };
        }

        productTotals[productId].quantity += line.qty || 0;
        productTotals[productId].amount += line.price_subtotal || 0;
      });

      // Convert to array and sort by quantity
      const products = Object.values(productTotals)
        .sort((a, b) => b.quantity - a.quantity)
        .slice(0, 3); // Top 3 only

      // Calculate percentages for mini bars
      const maxQuantity = products.length > 0 ? products[0].quantity : 1;

      // Format and add ranking
      this.state.pos_top_products = products.map((product, index) => ({
        id: product.id,
        name: product.name,
        quantity: product.quantity,
        amount: this.formatCurrency(product.amount),
        rank: index + 1,
        percentage: maxQuantity > 0 ? (product.quantity / maxQuantity) * 100 : 0
      }));

    } catch (error) {
      console.error('Error fetching top selling products:', error);
      this.state.pos_top_products = [];
    }
  }

  // ===== PRICING SCENARIOS METHODS =====

  // Initialize pricing scenarios date range with default values
  initializePricingScenariosDateRange() {
    const today = new Date();
    const lastMonth = new Date(today.getFullYear(), today.getMonth() - 1, 1);
    const lastMonthEnd = new Date(today.getFullYear(), today.getMonth(), 0);

    // Set default date range to last month
    this.state.pricing_scenarios_start_date = this.formatDateForInput(lastMonth);
    this.state.pricing_scenarios_end_date = this.formatDateForInput(lastMonthEnd);
  }

  // Format date for HTML date input (YYYY-MM-DD)
  formatDateForInput(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  // Load pricing scenarios for selected date range
  async loadPricingScenarios(startDate = null, endDate = null) {
    const selectedStartDate = startDate || this.state.pricing_scenarios_start_date;
    const selectedEndDate = endDate || this.state.pricing_scenarios_end_date;

    if (!selectedStartDate || !selectedEndDate) {
      console.error('No date range selected for pricing scenarios');
      return;
    }

    this.state.pricing_scenarios_loading = true;
    this.state.pricing_scenarios_error = null;

    try {
      const response = await fetch(`/api/pricing-scenarios/date-range?start_date=${selectedStartDate}&end_date=${selectedEndDate}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();

      if (response.ok) {
        this.state.pricing_scenarios_data = data;
        this.state.pricing_scenarios_start_date = selectedStartDate;
        this.state.pricing_scenarios_end_date = selectedEndDate;
      } else {
        this.state.pricing_scenarios_error = data.message || 'Failed to load pricing scenarios';
        this.state.pricing_scenarios_data = null;
      }
    } catch (error) {
      console.error('Error loading pricing scenarios:', error);
      this.state.pricing_scenarios_error = 'Network error loading pricing scenarios';
      this.state.pricing_scenarios_data = null;
    } finally {
      this.state.pricing_scenarios_loading = false;
    }
  }

  // Calculate custom net scenario
  async calculateCustomNetScenario() {
    if (!this.state.pricing_scenarios_start_date || !this.state.pricing_scenarios_end_date) {
      console.error('No date range selected for custom scenario');
      return;
    }

    this.state.pricing_scenarios_loading = true;
    this.state.pricing_scenarios_error = null;

    try {
      const response = await fetch('/api/pricing-scenarios/custom', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          start_date: this.state.pricing_scenarios_start_date,
          end_date: this.state.pricing_scenarios_end_date,
          target: this.state.pricing_scenarios_custom_target
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // Update the custom scenario in existing data
        if (this.state.pricing_scenarios_data) {
          this.state.pricing_scenarios_data.scenarios.net_custom = data.scenarios.net_custom;
        }
      } else {
        this.state.pricing_scenarios_error = data.message || 'Failed to calculate custom scenario';
      }
    } catch (error) {
      console.error('Error calculating custom scenario:', error);
      this.state.pricing_scenarios_error = 'Network error calculating custom scenario';
    } finally {
      this.state.pricing_scenarios_loading = false;
    }
  }

  // Handle start date change
  onPricingScenariosStartDateChange(event) {
    this.state.pricing_scenarios_start_date = event.target.value;
  }

  // Handle end date change
  onPricingScenariosEndDateChange(event) {
    this.state.pricing_scenarios_end_date = event.target.value;
  }

  // Handle date range apply
  async onPricingScenariosDateRangeChange() {
    if (!this.state.pricing_scenarios_start_date || !this.state.pricing_scenarios_end_date) {
      this.showToast('Please select both start and end dates.', 'error');
      return;
    }

    // Validate date range
    const startDate = new Date(this.state.pricing_scenarios_start_date);
    const endDate = new Date(this.state.pricing_scenarios_end_date);

    if (startDate > endDate) {
      this.showToast('Start date cannot be after end date.', 'error');
      return;
    }

    await this.loadPricingScenarios();
  }

  // Handle tab change
  onPricingScenariosTabChange(tab) {
    this.state.pricing_scenarios_current_tab = tab;
  }

  // Handle weighting mode change
  onPricingScenariosWeightingModeChange(mode) {
    this.state.pricing_scenarios_weighting_mode = mode;
  }

  // Handle custom target change
  onPricingScenariosCustomTargetChange(target) {
    this.state.pricing_scenarios_custom_target = parseFloat(target) || 0;
  }

  // Format currency for pricing scenarios
  formatPricingCurrency(amount) {
    return new Intl.NumberFormat('en-AE', {
      style: 'currency',
      currency: 'AED',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(amount);
  }

  // Format percentage for pricing scenarios
  formatPricingPercentage(value) {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  }

  // Get current scenario data based on tab and weighting mode
  getCurrentScenarioData() {
    if (!this.state.pricing_scenarios_data || !this.state.pricing_scenarios_data.scenarios) {
      return [];
    }

    const scenarios = this.state.pricing_scenarios_data.scenarios;

    switch (this.state.pricing_scenarios_current_tab) {
      case 'break_even':
        return scenarios.break_even || [];

      case 'net_10k':
        if (this.state.pricing_scenarios_weighting_mode === 'uniform') {
          return scenarios.net_10k?.uniform?.rows || [];
        } else {
          return scenarios.net_10k?.weighted?.rows || [];
        }

      case 'net_custom':
        if (this.state.pricing_scenarios_weighting_mode === 'uniform') {
          return scenarios.net_custom?.uniform?.rows || [];
        } else {
          return scenarios.net_custom?.weighted?.rows || [];
        }

      default:
        return [];
    }
  }

  // Get scenario metadata (uplifts, warnings, etc.)
  getCurrentScenarioMetadata() {
    if (!this.state.pricing_scenarios_data || !this.state.pricing_scenarios_data.scenarios) {
      return null;
    }

    const scenarios = this.state.pricing_scenarios_data.scenarios;

    switch (this.state.pricing_scenarios_current_tab) {
      case 'net_10k':
        if (this.state.pricing_scenarios_weighting_mode === 'uniform') {
          return {
            x: scenarios.net_10k?.uniform?.x,
            unrealistic: scenarios.net_10k?.uniform?.unrealistic
          };
        } else {
          return {
            x_budget: scenarios.net_10k?.weighted?.x_budget,
            x_range: scenarios.net_10k?.weighted?.x_range,
            unrealistic: scenarios.net_10k?.weighted?.unrealistic
          };
        }

      case 'net_custom':
        if (this.state.pricing_scenarios_weighting_mode === 'uniform') {
          return {
            x: scenarios.net_custom?.uniform?.x,
            unrealistic: scenarios.net_custom?.uniform?.unrealistic
          };
        } else {
          return {
            x_budget: scenarios.net_custom?.weighted?.x_budget,
            x_range: scenarios.net_custom?.weighted?.x_range,
            unrealistic: scenarios.net_custom?.weighted?.unrealistic
          };
        }

      default:
        return null;
    }
  }

  // Action button methods
  async applyPricingChanges() {
    const currentTab = this.state.pricing_scenarios_current_tab;
    const mode = this.state.pricing_scenarios_weighting_mode;
    const startDate = this.state.pricing_scenarios_start_date;
    const endDate = this.state.pricing_scenarios_end_date;

    if (!startDate || !endDate) {
      this.state.pricing_scenarios_error = 'Please select a date range first.';
      return;
    }

    try {
      this.state.pricing_scenarios_loading = true;
      this.state.pricing_scenarios_error = null;

      // Generate idempotency key
      const idempotencyKey = this.generateIdempotencyKey();

      const payload = {
        start_date: startDate,
        end_date: endDate,
        scenario: currentTab,
        mode: mode,
        dry_run: false, // Create actual price list
        idempotency_key: idempotencyKey
      };

      // Add target for custom scenarios
      if (currentTab === 'net_custom') {
        const target = parseFloat(this.state.pricing_scenarios_custom_target);
        if (!target || target <= 0) {
          this.state.pricing_scenarios_error = 'Please enter a valid custom target amount.';
          return;
        }
        payload.target = target;
      }

      const response = await fetch('/api/pricing-scenarios/apply', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      const result = await response.json();

      if (result.status === 'draft') {
        // Show success message and offer to activate
        this.showPriceListCreated(result);
      } else if (result.status === 'error') {
        this.state.pricing_scenarios_error = result.message;
      } else {
        this.state.pricing_scenarios_error = 'Unexpected response from server.';
      }

    } catch (error) {
      console.error('Error applying pricing changes:', error);
      this.state.pricing_scenarios_error = 'Failed to apply pricing changes. Please try again.';
    } finally {
      this.state.pricing_scenarios_loading = false;
    }
  }

  async previewPricingChanges() {
    const currentTab = this.state.pricing_scenarios_current_tab;
    const mode = this.state.pricing_scenarios_weighting_mode;
    const startDate = this.state.pricing_scenarios_start_date;
    const endDate = this.state.pricing_scenarios_end_date;

    if (!startDate || !endDate) {
      this.state.pricing_scenarios_error = 'Please select a date range first.';
      return;
    }

    try {
      this.state.pricing_scenarios_loading = true;
      this.state.pricing_scenarios_error = null;

      const payload = {
        start_date: startDate,
        end_date: endDate,
        scenario: currentTab,
        mode: mode,
        dry_run: true // Preview only
      };

      // Add target for custom scenarios
      if (currentTab === 'net_custom') {
        const target = parseFloat(this.state.pricing_scenarios_custom_target);
        if (!target || target <= 0) {
          this.state.pricing_scenarios_error = 'Please enter a valid custom target amount.';
          return;
        }
        payload.target = target;
      }

      const response = await fetch('/api/pricing-scenarios/apply', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      const result = await response.json();

      if (result.status === 'preview') {
        this.showPricingPreview(result);
      } else if (result.status === 'error') {
        this.state.pricing_scenarios_error = result.message;
      } else {
        this.state.pricing_scenarios_error = 'Unexpected response from server.';
      }

    } catch (error) {
      console.error('Error previewing pricing changes:', error);
      this.state.pricing_scenarios_error = 'Failed to preview pricing changes. Please try again.';
    } finally {
      this.state.pricing_scenarios_loading = false;
    }
  }

  generateIdempotencyKey() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
      const r = Math.random() * 16 | 0;
      const v = c == 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  showPriceListCreated(result) {
    // Show notification or modal with price list details
    const message = `Price list created successfully!\n\n` +
      `Products: ${result.summary.products}\n` +
      `Min Change: ${(result.summary.min_pct * 100).toFixed(2)}%\n` +
      `Max Change: ${(result.summary.max_pct * 100).toFixed(2)}%\n` +
      `Floors Applied: ${result.summary.floors_triggered}`;

    // You can implement a proper notification system here
    alert(message);
  }

  showPricingPreview(result) {
    // Show preview modal or notification
    const message = `Pricing Preview:\n\n` +
      `Products: ${result.summary.products}\n` +
      `Min Change: ${(result.summary.min_pct * 100).toFixed(2)}%\n` +
      `Max Change: ${(result.summary.max_pct * 100).toFixed(2)}%\n` +
      `Floors Applied: ${result.summary.floors_triggered}`;

    // You can implement a proper preview modal here
    alert(message);
  }

  // Show toast notification
  showToast(message, type = 'info') {
    // Simple toast implementation - you can enhance this with a proper toast library
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: ${type === 'error' ? '#f44336' : type === 'success' ? '#4caf50' : '#2196f3'};
      color: white;
      padding: 12px 20px;
      border-radius: 4px;
      z-index: 10000;
      box-shadow: 0 2px 8px rgba(0,0,0,0.2);
      font-size: 14px;
      max-width: 300px;
    `;

    document.body.appendChild(toast);

    // Auto remove after 5 seconds
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 5000);
  }

  // ===== NEW COMPREHENSIVE DATA METHODS =====

  // Get complete monthly sales data
  async getCompleteMonthlySalesData(monthStart, monthEnd) {
    try {
      const result = await this.orm.call('pos.order', 'get_complete_monthly_sales_data', [monthStart, monthEnd]);
      return result;
    } catch (error) {
      console.error('Error getting complete monthly sales data:', error);
      this.showToast('Error loading sales data', 'error');
      return null;
    }
  }

  // Get product performance analysis
  async getProductPerformanceAnalysis(monthStart, monthEnd) {
    try {
      const result = await this.orm.call('pos.order', 'get_product_performance_analysis', [monthStart, monthEnd]);
      return result;
    } catch (error) {
      console.error('Error getting product performance analysis:', error);
      this.showToast('Error loading performance analysis', 'error');
      return null;
    }
  }

  // Get category analysis
  async getCategoryAnalysis(monthStart, monthEnd) {
    try {
      const result = await this.orm.call('pos.order', 'get_category_analysis', [monthStart, monthEnd]);
      return result;
    } catch (error) {
      console.error('Error getting category analysis:', error);
      this.showToast('Error loading category analysis', 'error');
      return null;
    }
  }

  // Export monthly sales data
  async exportMonthlySalesData(monthStart, monthEnd, format = 'csv') {
    try {
      const result = await this.orm.call('pos.order', 'export_monthly_sales_data', [monthStart, monthEnd, format]);

      if (result) {
        // Create download link
        const blob = new Blob([result], {
          type: format === 'csv' ? 'text/csv' :
            format === 'excel' ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' :
              'application/json'
        });

        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `monthly_sales_${monthStart}_to_${monthEnd}.${format === 'excel' ? 'xlsx' : format}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);

        this.showToast(`Data exported successfully as ${format.toUpperCase()}`, 'success');
      }
    } catch (error) {
      console.error('Error exporting data:', error);
      this.showToast('Error exporting data', 'error');
    }
  }

  // Display comprehensive product data in a modal
  async showCompleteProductData(monthStart, monthEnd) {
    try {
      const data = await this.getCompleteMonthlySalesData(monthStart, monthEnd);

      if (!data) return;

      // Create modal content
      const modalContent = this.createProductDataModal(data);

      // Show modal (you can implement your own modal system)
      this.showModal('Complete Product Sales Data', modalContent);

    } catch (error) {
      console.error('Error showing complete product data:', error);
      this.showToast('Error loading product data', 'error');
    }
  }

  // Create modal content for product data
  createProductDataModal(data) {
    const { products, total_products, total_revenue, total_quantity } = data;

    let html = `
      <div class="product-data-modal">
        <div class="summary-stats">
          <div class="stat-card">
            <h4>Total Products</h4>
            <span class="stat-value">${total_products}</span>
          </div>
          <div class="stat-card">
            <h4>Total Revenue</h4>
            <span class="stat-value">${this.formatCurrency(total_revenue)}</span>
          </div>
          <div class="stat-card">
            <h4>Total Quantity</h4>
            <span class="stat-value">${total_quantity}</span>
          </div>
        </div>
        
        <div class="export-buttons">
          <button class="btn btn-primary" onclick="this.exportMonthlySalesData('${data.month_start}', '${data.month_end}', 'csv')">
            Export CSV
          </button>
          <button class="btn btn-success" onclick="this.exportMonthlySalesData('${data.month_start}', '${data.month_end}', 'excel')">
            Export Excel
          </button>
          <button class="btn btn-info" onclick="this.exportMonthlySalesData('${data.month_start}', '${data.month_end}', 'json')">
            Export JSON
          </button>
        </div>
        
        <div class="product-table-container">
          <table class="modern-table">
            <thead>
              <tr>
                <th>Product Name</th>
                <th>SKU</th>
                <th>Category</th>
                <th>Quantity</th>
                <th>Avg Price</th>
                <th>Revenue</th>
                <th>Margin %</th>
                <th>Stock</th>
                <th>Turnover</th>
              </tr>
            </thead>
            <tbody>
    `;

    products.forEach(product => {
      html += `
        <tr>
          <td>${product.product_name}</td>
          <td>${product.sku || '-'}</td>
          <td>${product.category_name}</td>
          <td>${product.total_quantity}</td>
          <td>${this.formatCurrency(product.avg_price)}</td>
          <td>${this.formatCurrency(product.total_revenue)}</td>
          <td class="${product.margin_percentage >= 20 ? 'text-success' : product.margin_percentage >= 10 ? 'text-warning' : 'text-danger'}">
            ${product.margin_percentage.toFixed(1)}%
          </td>
          <td>${product.current_stock}</td>
          <td>${product.turnover_ratio.toFixed(2)}</td>
        </tr>
      `;
    });

    html += `
            </tbody>
          </table>
        </div>
      </div>
    `;

    return html;
  }

  // Simple modal implementation
  showModal(title, content) {
    // Remove existing modal if any
    const existingModal = document.querySelector('.custom-modal');
    if (existingModal) {
      existingModal.remove();
    }

    const modal = document.createElement('div');
    modal.className = 'custom-modal';
    modal.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0,0,0,0.5);
      z-index: 10000;
      display: flex;
      align-items: center;
      justify-content: center;
    `;

    const modalContent = document.createElement('div');
    modalContent.style.cssText = `
      background: white;
      border-radius: 8px;
      max-width: 90%;
      max-height: 90%;
      overflow: auto;
      box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    `;

    modalContent.innerHTML = `
      <div class="modal-header" style="padding: 20px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center;">
        <h3 style="margin: 0;">${title}</h3>
        <button class="close-modal" style="background: none; border: none; font-size: 24px; cursor: pointer;">&times;</button>
      </div>
      <div class="modal-body" style="padding: 20px;">
        ${content}
      </div>
    `;

    modal.appendChild(modalContent);
    document.body.appendChild(modal);

    // Close modal handlers
    const closeModal = () => modal.remove();
    modalContent.querySelector('.close-modal').onclick = closeModal;
    modal.onclick = (e) => {
      if (e.target === modal) closeModal();
    };

    // Add some basic styling
    const style = document.createElement('style');
    style.textContent = `
      .product-data-modal .summary-stats {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin-bottom: 20px;
      }
      .product-data-modal .stat-card {
        background: #f8f9fa;
        padding: 16px;
        border-radius: 8px;
        text-align: center;
      }
      .product-data-modal .stat-card h4 {
        margin: 0 0 8px 0;
        color: #666;
        font-size: 14px;
      }
      .product-data-modal .stat-value {
        font-size: 24px;
        font-weight: bold;
        color: #2c3e50;
      }
      .product-data-modal .export-buttons {
        margin-bottom: 20px;
        text-align: center;
      }
      .product-data-modal .export-buttons .btn {
        margin: 0 8px;
        padding: 8px 16px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
      }
      .product-data-modal .export-buttons .btn-primary {
        background: #007bff;
        color: white;
      }
      .product-data-modal .export-buttons .btn-success {
        background: #28a745;
        color: white;
      }
      .product-data-modal .export-buttons .btn-info {
        background: #17a2b8;
        color: white;
      }
      .product-data-modal .product-table-container {
        max-height: 400px;
        overflow-y: auto;
      }
      .product-data-modal .modern-table {
        width: 100%;
        border-collapse: collapse;
      }
      .product-data-modal .modern-table th,
      .product-data-modal .modern-table td {
        padding: 8px 12px;
        text-align: left;
        border-bottom: 1px solid #eee;
      }
      .product-data-modal .modern-table th {
        background: #f8f9fa;
        font-weight: 600;
      }
      .product-data-modal .text-success {
        color: #28a745;
      }
      .product-data-modal .text-warning {
        color: #ffc107;
      }
      .product-data-modal .text-danger {
        color: #dc3545;
      }
    `;
    document.head.appendChild(style);
  }
}
PosDashboard.template = 'PosDashboard'
registry.category("actions").add("pos_order_menu", PosDashboard)
